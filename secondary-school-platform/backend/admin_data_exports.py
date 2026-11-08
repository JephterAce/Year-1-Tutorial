"""Administrator request, two-person approval and download controls for private exports."""
from uuid import UUID

from flask import Blueprint, current_app, jsonify, request
from psycopg.types.json import Jsonb

from admin_policy import require
from database import connection

admin_exports = Blueprint("admin_exports", __name__)


def _admin(capability, csrf=False):
    from admin_auth import authenticate_admin, validate_admin_csrf
    session = authenticate_admin(request.cookies.get("learnwise_admin_session"))
    if not session:
        return None, (jsonify({"error": "unauthenticated"}), 401)
    if csrf and not validate_admin_csrf(session, request.headers.get("X-CSRF-Token", "")):
        return None, (jsonify({"error": "csrf_failed"}), 401)
    try:
        require(session["principal"], capability)
    except PermissionError:
        return None, (jsonify({"error": "forbidden"}), 403)
    return session, None


def _uuid(value):
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        return None


@admin_exports.post("/api/v1/admin/data-exports")
def request_export():
    session, error = _admin("export.request", csrf=True)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    from export_policy import validate_export_request
    try:
        spec = validate_export_request(data)
    except ValueError as exc:
        return jsonify({"error": "invalid_export_request", "message": str(exc)}), 400

    if spec.subject_slugs:
        return jsonify({"error": "subject_scoped_bulk_export_not_supported"}), 400
    if spec.scope == "bulk":
        if not spec.class_levels and not (spec.date_from and spec.date_to):
            return jsonify({"error": "bulk_export_requires_a_class_or_date_filter"}), 400
        if data.get("confirm_bulk") is not True:
            return jsonify({"error": "bulk_export_confirmation_required"}), 400

    target_id = spec.student_id
    try:
        with connection() as conn:
            if target_id:
                exists = conn.execute("SELECT 1 FROM students WHERE id=%s", (target_id,)).fetchone()
                if not exists:
                    return jsonify({"error": "student_not_found"}), 404
            filters = {
                "class_levels": list(spec.class_levels),
                "subject_slugs": list(spec.subject_slugs),
                "date_from": spec.date_from,
                "date_to": spec.date_to,
            }
            row = conn.execute(
                """INSERT INTO student_data_exports(
                     requested_by_admin_id,target_student_id,export_scope,export_format,filters
                   ) VALUES (%s,%s,%s,%s,%s)
                   RETURNING id,status,requested_at""",
                (session["admin_id"], target_id, spec.scope, spec.export_format, Jsonb(filters)),
            ).fetchone()
            conn.execute(
                """INSERT INTO student_data_export_audit(
                     export_id,actor_admin_id,event_type,source_ip,details
                   ) VALUES (%s,%s,'requested',%s,%s)""",
                (row["id"], session["admin_id"], request.remote_addr,
                 Jsonb({"scope": spec.scope, "format": spec.export_format})),
            )
        return jsonify({
            "export": {
                "id": str(row["id"]), "status": row["status"],
                "requested_at": row["requested_at"].isoformat(),
                "approval_required": True,
            }
        }), 201
    except Exception:
        current_app.logger.exception("Admin data export request failed")
        return jsonify({"error": "export_request_unavailable"}), 503


@admin_exports.get("/api/v1/admin/data-exports")
def list_exports():
    session, error = _admin("export.request")
    if error:
        return error
    try:
        with connection() as conn:
            rows = conn.execute(
                """SELECT id,requested_by_admin_id,approved_by_admin_id,approved_at,
                          target_student_id,export_scope,export_format,filters,status,
                          record_count,checksum_sha256,requested_at,completed_at,expires_at,
                          failure_code,attempt_count
                   FROM student_data_exports
                   ORDER BY requested_at DESC LIMIT 100"""
            ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            for key in ("id", "requested_by_admin_id", "approved_by_admin_id", "target_student_id"):
                if item.get(key) is not None:
                    item[key] = str(item[key])
            for key in ("approved_at", "requested_at", "completed_at", "expires_at"):
                if item.get(key) is not None:
                    item[key] = item[key].isoformat()
            items.append(item)
        return jsonify({"items": items}), 200
    except Exception:
        current_app.logger.exception("Admin data export list failed")
        return jsonify({"error": "export_list_unavailable"}), 503


@admin_exports.post("/api/v1/admin/data-exports/<export_id>/approve")
def approve_export(export_id):
    session, error = _admin("export.approve", csrf=True)
    if error:
        return error
    export_id = _uuid(export_id)
    if not export_id:
        return jsonify({"error": "invalid_export_id"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """UPDATE student_data_exports
                   SET approved_by_admin_id=%s,approved_at=now()
                   WHERE id=%s AND status='queued' AND approved_at IS NULL
                     AND requested_by_admin_id<>%s
                   RETURNING id,requested_by_admin_id,export_scope,export_format""",
                (session["admin_id"], export_id, session["admin_id"]),
            ).fetchone()
            if not row:
                return jsonify({"error": "export_not_approvable_or_separate_approver_required"}), 409
            conn.execute(
                """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
                   VALUES (%s,%s,'authorised',%s)""",
                (export_id, session["admin_id"],
                 Jsonb({"scope": row["export_scope"], "format": row["export_format"]})),
            )
        return jsonify({"export_id": export_id, "approved": True}), 200
    except Exception:
        current_app.logger.exception("Admin data export approval failed")
        return jsonify({"error": "export_approval_unavailable"}), 503


@admin_exports.post("/api/v1/admin/data-exports/<export_id>/retry")
def retry_export(export_id):
    session, error = _admin("export.approve", csrf=True)
    if error:
        return error
    export_id = _uuid(export_id)
    if not export_id:
        return jsonify({"error": "invalid_export_id"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """UPDATE student_data_exports
                   SET status='queued',failure_code=NULL,started_at=NULL
                   WHERE id=%s AND status='failed' AND attempt_count<3
                     AND approved_at IS NOT NULL AND approved_by_admin_id<>%s
                   RETURNING id""",
                (export_id, session["admin_id"]),
            ).fetchone()
            if not row:
                return jsonify({"error": "export_not_retryable"}), 409
            conn.execute(
                """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
                   VALUES (%s,%s,'authorised','{"action":"retry"}'::jsonb)""",
                (export_id, session["admin_id"]),
            )
        return jsonify({"export_id": export_id, "requeued": True}), 200
    except Exception:
        current_app.logger.exception("Admin data export retry failed")
        return jsonify({"error": "export_retry_unavailable"}), 503


@admin_exports.get("/api/v1/admin/data-exports/<export_id>/download")
def download_export():
    session, error = _admin("export.download")
    if error:
        return error
    export_id = _uuid(request.view_args.get("export_id"))
    if not export_id:
        return jsonify({"error": "invalid_export_id"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """SELECT requested_by_admin_id,status,expires_at
                   FROM student_data_exports WHERE id=%s""",
                (export_id,),
            ).fetchone()
            if not row or (str(row["requested_by_admin_id"]) != session["admin_id"] and session["role"] != "owner"):
                return jsonify({"error": "export_not_available"}), 404
            if row["status"] != "completed" or not row["expires_at"]:
                return jsonify({"error": "export_not_available"}), 404
        from student_bulk_export import create_export_download_url, ExportWorkerError
        urls = create_export_download_url(export_id)
        with connection() as conn:
            conn.execute(
                """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
                   VALUES (%s,%s,'downloaded','{"signed_url_ttl_seconds":300}'::jsonb)""",
                (export_id, session["admin_id"]),
            )
        return jsonify(urls), 200
    except ExportWorkerError:
        return jsonify({"error": "export_not_available"}), 404
    except Exception:
        current_app.logger.exception("Admin data export download failed")
        return jsonify({"error": "export_download_unavailable"}), 503


@admin_exports.post("/api/v1/admin/data-exports/<export_id>/cancel")
def cancel_export(export_id):
    session, error = _admin("export.request", csrf=True)
    if error:
        return error
    export_id = _uuid(export_id)
    if not export_id:
        return jsonify({"error": "invalid_export_id"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """UPDATE student_data_exports SET status='cancelled'
                   WHERE id=%s AND status='queued' AND approved_at IS NULL
                     AND requested_by_admin_id=%s RETURNING id""",
                (export_id, session["admin_id"]),
            ).fetchone()
            if not row:
                return jsonify({"error": "export_not_cancellable"}), 409
            conn.execute(
                """INSERT INTO student_data_export_audit(export_id,actor_admin_id,event_type,details)
                   VALUES (%s,%s,'cancelled','{}'::jsonb)""",
                (export_id, session["admin_id"]),
            )
        return jsonify({"export_id": export_id, "cancelled": True}), 200
    except Exception:
        current_app.logger.exception("Admin data export cancellation failed")
        return jsonify({"error": "export_cancel_unavailable"}), 503
