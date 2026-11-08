"""Approved, bounded, private student export worker.

Jobs are processed only after a different administrator approves them. The worker
uses a repeatable-read, read-only PostgreSQL snapshot and multipart S3 upload; it
never writes student data to the repository or application logs.
"""
import csv
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import UUID

import boto3
from botocore.config import Config
from psycopg.types.json import Jsonb

from database import connection
from export_serialization import _csv_safe, _json_value
from student_data_export import build_student_export

PART_SIZE = 8 * 1024 * 1024
MAX_BULK_ROWS = 100_000
EXPORT_TTL_HOURS = 24


class ExportWorkerError(RuntimeError):
    pass


def _storage():
    cfg = {
        "access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "endpoint_url": os.environ.get("AWS_ENDPOINT_URL_S3", ""),
        "region": os.environ.get("AWS_REGION", ""),
        "bucket": os.environ.get("DATA_EXPORT_STORAGE_BUCKET", ""),
    }
    if not all(isinstance(v, str) and v.strip() for v in cfg.values()):
        raise ExportWorkerError("private_export_storage_not_configured")
    if not cfg["endpoint_url"].startswith("https://"):
        raise ExportWorkerError("private_export_storage_requires_https")
    client = boto3.client(
        "s3", endpoint_url=cfg["endpoint_url"], region_name=cfg["region"],
        aws_access_key_id=cfg["access_key_id"],
        aws_secret_access_key=cfg["secret_access_key"],
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    return client, cfg["bucket"]


def _audit(conn, job, event_type, details=None):
    conn.execute(
        """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
           VALUES (%s,%s,%s,%s)""",
        (job["id"], job["requested_by_admin_id"], event_type, Jsonb(details or {})),
    )


def _claim_job():
    with connection() as conn:
        row = conn.execute(
            """UPDATE student_data_exports
               SET status='processing',started_at=now(),last_attempt_at=now(),
                   attempt_count=attempt_count+1,failure_code=NULL
               WHERE id=(
                 SELECT id FROM student_data_exports
                 WHERE approved_at IS NOT NULL AND attempt_count < 3
                   AND (status='queued' OR
                        (status='processing' AND started_at < now()-interval '2 hours'))
                 ORDER BY requested_at
                 FOR UPDATE SKIP LOCKED LIMIT 1
               )
               RETURNING *"""
        ).fetchone()
        if row:
            _audit(conn, row, "started", {"actor": "worker", "attempt": row["attempt_count"]})
        return dict(row) if row else None


def _multipart_upload(client, bucket, key, chunks, content_type, export_id):
    created = client.create_multipart_upload(
        Bucket=bucket, Key=key, ContentType=content_type,
        Metadata={"export-id": str(export_id), "classification": "restricted"},
    )
    upload_id = created["UploadId"]
    parts, buffer, digest, size = [], bytearray(), hashlib.sha256(), 0

    def send_part(data, number):
        response = client.upload_part(
            Bucket=bucket, Key=key, UploadId=upload_id,
            PartNumber=number, Body=data,
        )
        parts.append({"PartNumber": number, "ETag": response["ETag"]})

    try:
        for chunk in chunks:
            if not isinstance(chunk, (bytes, bytearray)):
                raise ExportWorkerError("invalid_export_chunk")
            if not chunk:
                continue
            digest.update(chunk)
            size += len(chunk)
            buffer.extend(chunk)
            while len(buffer) >= PART_SIZE:
                send_part(bytes(buffer[:PART_SIZE]), len(parts) + 1)
                del buffer[:PART_SIZE]
        if not parts and not buffer:
            client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
            client.put_object(
                Bucket=bucket, Key=key, Body=b"", ContentType=content_type,
                Metadata={"export-id": str(export_id), "classification": "restricted"},
            )
            return digest.hexdigest(), 0
        if buffer:
            send_part(bytes(buffer), len(parts) + 1)
        client.complete_multipart_upload(
            Bucket=bucket, Key=key, UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )
        return digest.hexdigest(), size
    except Exception:
        try:
            client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
        except Exception:
            pass
        raise


def _student_query(filters):
    clauses, params = [], []
    classes = filters.get("class_levels") or []
    if classes:
        clauses.append("class_level = ANY(%s)")
        params.append(classes)
    date_from, date_to = filters.get("date_from"), filters.get("date_to")
    if date_from and date_to:
        clauses.append("created_at >= %s::date")
        params.append(date_from)
        clauses.append("created_at < (%s::date + interval '1 day')")
        params.append(date_to)
    return (
        "SELECT id FROM students" + (" WHERE " + " AND ".join(clauses) if clauses else "") +
        " ORDER BY id",
        params,
    )


def _export_chunks(conn, job, generated_at):
    filters = job["filters"] or {}
    if filters.get("subject_slugs"):
        raise ExportWorkerError("subject_scoped_bulk_export_not_supported")
    if job["export_scope"] == "individual":
        query, params = "SELECT id FROM students WHERE id=%s ORDER BY id", [job["target_student_id"]]
    else:
        query, params = _student_query(filters)

    cursor = conn.cursor(name="think_tank_export_students")
    cursor.itersize = 250
    cursor.execute(query, params)
    count = 0
    if job["export_format"] == "csv":
        header = "student_id,email,display_name,username,class_level,record_json\n"
        yield header.encode("utf-8")
    for row in cursor:
        count += 1
        if count > MAX_BULK_ROWS:
            raise ExportWorkerError("export_row_limit_exceeded")
        payload = build_student_export(str(row["id"]), conn=conn)
        record = _json_value(payload)
        if job["export_format"] == "json":
            yield (json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
        else:
            student = record["student"]
            output = io.StringIO(newline="")
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow([
                _csv_safe(student.get("id")), _csv_safe(student.get("email")),
                _csv_safe(student.get("display_name")), _csv_safe(student.get("username")),
                _csv_safe(student.get("class_level")),
                _csv_safe(json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=False)),
            ])
            yield output.getvalue().encode("utf-8")
    cursor.close()
    return count


def process_one_export():
    job = _claim_job()
    if not job:
        return False
    try:
        client, bucket = _storage()
        export_id = str(UUID(str(job["id"])))
        attempt = int(job["attempt_count"])
        extension = "jsonl" if job["export_format"] == "json" else "csv"
        data_key = f"exports/{export_id}/attempt-{attempt}/data.{extension}"
        manifest_key = f"exports/{export_id}/attempt-{attempt}/manifest.json"
        generated_at = datetime.now(timezone.utc)
        ttl_hours = min(max(int(os.environ.get("DATA_EXPORT_TTL_HOURS", "24")), 1), EXPORT_TTL_HOURS)
        expires_at = generated_at + timedelta(hours=ttl_hours)

        with connection() as snapshot_conn:
            snapshot_conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            # The first query establishes the repeatable-read snapshot before streaming.
            snapshot_conn.execute("SELECT 1").fetchone()
            chunks = _export_chunks(snapshot_conn, job, generated_at)
            content_type = "application/x-ndjson" if job["export_format"] == "json" else "text/csv; charset=utf-8"
            checksum, byte_count = _multipart_upload(
                client, bucket, data_key, chunks, content_type, export_id
            )
            manifest = {
                "export_version": "1.0",
                "export_id": export_id,
                "scope": job["export_scope"],
                "format": job["export_format"],
                "filters": job["filters"] or {},
                "record_count": None,
                "generated_at": generated_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "data_object": data_key,
                "byte_count": byte_count,
                "sha256": checksum,
                "consistency": "single repeatable-read, read-only PostgreSQL snapshot",
            }
            count_query = "SELECT count(*) AS n FROM students"
            count_params = []
            if job["export_scope"] == "individual":
                count_query += " WHERE id=%s"
                count_params.append(job["target_student_id"])
            else:
                count_query, count_params = _student_query(job["filters"] or {})
                count_query = "SELECT count(*) AS n FROM (" + count_query + ") AS selected_students"
            manifest["record_count"] = int(snapshot_conn.execute(count_query, count_params).fetchone()["n"])
            client.put_object(
                Bucket=bucket, Key=manifest_key,
                Body=json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                ContentType="application/json",
                Metadata={"export-id": export_id, "classification": "restricted"},
            )
        # Persist completion only after both private objects exist and the read snapshot closes.
        with connection() as conn:
            conn.execute(
                """UPDATE student_data_exports
                   SET status='completed',storage_key=%s,manifest_storage_key=%s,
                       checksum_sha256=%s,record_count=%s,completed_at=now(),
                       expires_at=%s,failure_code=NULL
                   WHERE id=%s AND status='processing'""",
                (data_key, manifest_key, checksum, manifest["record_count"], expires_at, job["id"]),
            )
            _audit(conn, job, "completed", {
                "actor": "worker", "record_count": manifest["record_count"], "byte_count": byte_count,
                "sha256": checksum, "expires_at": expires_at.isoformat(),
            })
        return True
    except Exception as exc:
        code = exc.args[0] if isinstance(exc, ExportWorkerError) and exc.args else "export_processing_failed"
        safe_code = code if isinstance(code, str) and code.replace("_", "").isalnum() else "export_processing_failed"
        with connection() as conn:
            conn.execute(
                """UPDATE student_data_exports SET status='failed',failure_code=%s
                   WHERE id=%s AND status='processing'""",
                (safe_code[:80], job["id"]),
            )
            _audit(conn, job, "failed", {"actor": "worker", "failure_code": safe_code[:80]})
        return False


def create_export_download_url(export_id, ttl_seconds=300):
    try:
        export_id = str(UUID(str(export_id)))
    except (TypeError, ValueError, AttributeError):
        raise ExportWorkerError("invalid_export_id") from None
    client, bucket = _storage()
    with connection() as conn:
        row = conn.execute(
            """SELECT storage_key,manifest_storage_key,expires_at,status
               FROM student_data_exports WHERE id=%s""",
            (export_id,),
        ).fetchone()
    if not row or row["status"] != "completed" or not row["expires_at"] or row["expires_at"] <= datetime.now(timezone.utc):
        raise ExportWorkerError("export_not_available")
    remaining = int((row["expires_at"] - datetime.now(timezone.utc)).total_seconds())
    if remaining <= 0:
        raise ExportWorkerError("export_not_available")
    ttl = min(max(int(ttl_seconds), 1), 300, remaining)
    data_url = client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": row["storage_key"]},
        ExpiresIn=ttl,
    )
    manifest_url = client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": row["manifest_storage_key"]},
        ExpiresIn=ttl,
    )
    return {"data_url": data_url, "manifest_url": manifest_url, "expires_in": ttl}


def expire_completed_exports(limit=50):
    client, bucket = _storage()
    with connection() as conn:
        rows = conn.execute(
            """SELECT id,requested_by_admin_id,storage_key,manifest_storage_key
               FROM student_data_exports
               WHERE status='completed' AND expires_at<=now()
               ORDER BY expires_at FOR UPDATE SKIP LOCKED LIMIT %s""",
            (max(1, min(int(limit), 100)),),
        ).fetchall()
        expired = 0
        for row in rows:
            try:
                for key in (row["storage_key"], row["manifest_storage_key"]):
                    if key:
                        client.delete_object(Bucket=bucket, Key=key)
                conn.execute(
                    "UPDATE student_data_exports SET status='expired' WHERE id=%s",
                    (row["id"],),
                )
                conn.execute(
                    """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
                       VALUES (%s,%s,'expired','{}'::jsonb)""",
                    (row["id"], row["requested_by_admin_id"]),
                )
                expired += 1
            except Exception:
                # Leave the row completed; the next expiry pass can retry deletion.
                continue
        return expired


if __name__ == "__main__":
    if os.environ.get("DATA_EXPORT_WORKER_ENABLED", "").strip().lower() not in {"1", "true", "yes"}:
        print("Data export worker is disabled; set DATA_EXPORT_WORKER_ENABLED only after storage and approval controls are verified.")
        raise SystemExit(2)
    action = sys.argv[1] if len(sys.argv) > 1 else "once"
    if action == "expire":
        print(f"Expired exports cleaned: {expire_completed_exports()}")
    elif action == "once":
        print("Export job processed." if process_one_export() else "No approved export processed.")
    else:
        print("Usage: python student_bulk_export.py [once|expire]", file=sys.stderr)
        raise SystemExit(2)
