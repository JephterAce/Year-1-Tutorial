"""Owner-triggered, staging-only private object-storage acceptance probes."""
from __future__ import annotations

import hashlib
import io
import os
import uuid
import wave

from botocore.config import Config
from botocore.exceptions import ClientError


class StorageAcceptanceError(RuntimeError):
    pass


def _synthetic_wav():
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\x00\x00" * 160)
    return output.getvalue()


def _status_code(exc):
    try:
        return int(exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))
    except Exception:
        return 0


def _unsigned_denied(endpoint, region, bucket, key):
    import boto3
    unsigned = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        config=Config(signature_version="unsigned", s3={"addressing_style": "path"}),
    )
    try:
        unsigned.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if _status_code(exc) in (401, 403):
            return True
        raise StorageAcceptanceError("Unsigned object access was not denied.") from None
    raise StorageAcceptanceError("Private object was readable without credentials.")


def _probe_s3(client, endpoint, region, bucket, key, payload):
    digest = hashlib.sha256(payload).hexdigest()
    result = {
        "configured": True,
        "upload": False,
        "retrieval": False,
        "checksum_match": False,
        "unsigned_access_denied": False,
        "deletion": False,
        "sha256": digest,
    }
    uploaded = False
    try:
        client.put_object(
            Bucket=bucket, Key=key, Body=payload,
            ContentType="audio/wav" if key.endswith(".wav") else "text/plain",
            Metadata={"purpose": "synthetic-staging-acceptance"},
        )
        uploaded = True
        result["upload"] = True
        retrieved = client.get_object(Bucket=bucket, Key=key)
        body = retrieved["Body"].read()
        try:
            retrieved["Body"].close()
        except Exception:
            pass
        result["retrieval"] = True
        result["checksum_match"] = hashlib.sha256(body).hexdigest() == digest
        if not result["checksum_match"]:
            raise StorageAcceptanceError("Retrieved object checksum did not match.")
        _unsigned_denied(endpoint, region, bucket, key)
        result["unsigned_access_denied"] = True
    finally:
        if uploaded:
            client.delete_object(Bucket=bucket, Key=key)
            try:
                client.head_object(Bucket=bucket, Key=key)
            except ClientError as exc:
                if _status_code(exc) == 404 or exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                    result["deletion"] = True
                else:
                    raise StorageAcceptanceError("Deleted object could not be verified absent.") from None
            else:
                raise StorageAcceptanceError("Synthetic object still exists after deletion.")
    return result


def _probe_audio(cfg, client, key, payload):
    from audio_storage import put_private_audio_object, get_private_audio_object, delete_private_audio_object
    digest = hashlib.sha256(payload).hexdigest()
    result = {
        "configured": True, "upload": False, "retrieval": False,
        "checksum_match": False, "unsigned_access_denied": False,
        "deletion": False, "sha256": digest,
    }
    uploaded = False
    try:
        put_private_audio_object(key, io.BytesIO(payload), "audio/wav", len(payload))
        uploaded = True
        result["upload"] = True
        stored = get_private_audio_object(key)
        body = stored["Body"].read()
        try:
            stored["Body"].close()
        except Exception:
            pass
        result["retrieval"] = True
        result["checksum_match"] = hashlib.sha256(body).hexdigest() == digest
        if not result["checksum_match"]:
            raise StorageAcceptanceError("Retrieved audio checksum did not match.")
        _unsigned_denied(cfg["endpoint_url"], cfg["region"], cfg["bucket"], key)
        result["unsigned_access_denied"] = True
    finally:
        if uploaded:
            delete_private_audio_object(key)
            try:
                client.head_object(Bucket=cfg["bucket"], Key=key)
            except ClientError as exc:
                if _status_code(exc) == 404 or exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                    result["deletion"] = True
                else:
                    raise StorageAcceptanceError("Deleted audio object could not be verified absent.") from None
            else:
                raise StorageAcceptanceError("Synthetic audio object still exists after deletion.")
    return result


def run_private_storage_acceptance():
    """Probe the configured private audio bucket and R2 export bucket independently."""
    if os.environ.get("APP_ENV", "").strip().lower() != "staging":
        raise StorageAcceptanceError("Storage acceptance is staging-only.")

    key_suffix = uuid.uuid4().hex
    payload = _synthetic_wav()
    results = {}

    try:
        from audio_storage import storage_config, _s3_client
        cfg = storage_config()
    except Exception as exc:
        results["audio"] = {
            "configured": False, "passed": False,
            "failure_phase": "audio_storage_configuration",
            "failure_class": type(exc).__name__[:80],
        }
    else:
        try:
            key = f"qa-acceptance/audio-{key_suffix}.wav"
            results["audio"] = _probe_audio(cfg, _s3_client(cfg), key, payload)
        except Exception as exc:
            results["audio"] = {
                "configured": True, "passed": False,
                "failure_phase": "audio_storage_transfer",
                "failure_class": type(exc).__name__[:80],
            }

    try:
        required = {
            "access_key_id": os.environ.get("DATA_EXPORT_AWS_ACCESS_KEY_ID", ""),
            "secret_access_key": os.environ.get("DATA_EXPORT_AWS_SECRET_ACCESS_KEY", ""),
            "endpoint": os.environ.get("DATA_EXPORT_AWS_ENDPOINT_URL_S3", ""),
            "region": os.environ.get("DATA_EXPORT_AWS_REGION", ""),
            "bucket": os.environ.get("DATA_EXPORT_STORAGE_BUCKET", ""),
        }
        if not all(isinstance(value, str) and value.strip() for value in required.values()):
            raise StorageAcceptanceError("R2 export storage is not configured.")
        if not required["endpoint"].startswith("https://"):
            raise StorageAcceptanceError("R2 endpoint must use HTTPS.")
        import boto3
        client = boto3.client(
            "s3",
            endpoint_url=required["endpoint"],
            region_name=required["region"],
            aws_access_key_id=required["access_key_id"],
            aws_secret_access_key=required["secret_access_key"],
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        key = f"qa-acceptance/export-{key_suffix}.wav"
        results["r2_exports"] = _probe_s3(
            client, required["endpoint"], required["region"], required["bucket"], key, payload
        )
    except Exception as exc:
        results["r2_exports"] = {
            "configured": False,
            "passed": False,
            "failure_phase": "r2_storage_probe",
            "failure_class": type(exc).__name__[:80],
        }

    for value in results.values():
        value["passed"] = all(
            value.get(field) is True
            for field in ("upload", "retrieval", "checksum_match", "unsigned_access_denied", "deletion")
        )
    return {
        "passed": all(value.get("passed") is True for value in results.values()),
        "results": results,
    }
