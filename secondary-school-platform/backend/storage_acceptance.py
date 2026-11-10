"""Owner-triggered, staging-only private object-storage acceptance probes."""
from __future__ import annotations

import hashlib
import io
import os
import re
import uuid
import wave

from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError


class StorageAcceptanceError(RuntimeError):
    pass


class StorageProbeStepError(RuntimeError):
    """Safe operation label for a failed synthetic storage probe step."""

    def __init__(self, failure_phase):
        self.failure_phase = failure_phase
        super().__init__("Private storage acceptance step failed.")


def _step(failure_phase, operation):
    try:
        return operation()
    except Exception as exc:
        raise StorageProbeStepError(failure_phase) from exc



def _safe_failure(exc, phase):
    """Return bounded diagnostic metadata only; never expose provider messages or credentials."""
    cause = exc
    while getattr(cause, "__cause__", None) is not None and cause.__cause__ is not cause:
        cause = cause.__cause__
    error = {
        "configured": True,
        "passed": False,
        "failure_phase": phase,
        "failure_class": type(cause).__name__[:80],
    }
    response = getattr(cause, "response", None)
    if isinstance(response, dict):
        details = response.get("Error", {})
        metadata = response.get("ResponseMetadata", {})
        code = details.get("Code") if isinstance(details, dict) else None
        status = metadata.get("HTTPStatusCode") if isinstance(metadata, dict) else None
        if isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,48}", code):
            error["provider_code"] = code
        if isinstance(status, int) and 100 <= status <= 599:
            error["http_status"] = status
            error["retryable"] = status == 429 or status >= 500
    if type(cause).__name__ in {"EndpointConnectionError", "ConnectTimeoutError", "ReadTimeoutError", "TimeoutError"}:
        error["retryable"] = True
    return error

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
        config=Config(signature_version=UNSIGNED, s3={"addressing_style": "path"}),
    )
    try:
        unsigned.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if _status_code(exc) in (401, 403):
            return True
        raise StorageAcceptanceError("Unsigned object access was not denied.") from exc
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
        _step("r2_upload", lambda: client.put_object(
            Bucket=bucket, Key=key, Body=payload,
            ContentType="audio/wav" if key.endswith(".wav") else "text/plain",
            Metadata={"purpose": "synthetic-staging-acceptance"},
        ))
        uploaded = True
        result["upload"] = True
        retrieved = _step("r2_retrieval", lambda: client.get_object(Bucket=bucket, Key=key))
        body = retrieved["Body"].read()
        try:
            retrieved["Body"].close()
        except Exception:
            pass
        result["retrieval"] = True
        result["checksum_match"] = hashlib.sha256(body).hexdigest() == digest
        if not result["checksum_match"]:
            raise StorageAcceptanceError("Retrieved object checksum did not match.")
        _step("r2_unsigned_access", lambda: _unsigned_denied(endpoint, region, bucket, key))
        result["unsigned_access_denied"] = True
    finally:
        if uploaded:
            _step("r2_deletion", lambda: client.delete_object(Bucket=bucket, Key=key))
            try:
                client.head_object(Bucket=bucket, Key=key)
            except ClientError as exc:
                if _status_code(exc) == 404 or exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                    result["deletion"] = True
                else:
                    raise StorageProbeStepError("r2_deletion_verify") from exc
            except Exception as exc:
                raise StorageProbeStepError("r2_deletion_verify") from exc
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
        _step("audio_upload", lambda: put_private_audio_object(key, io.BytesIO(payload), "audio/wav", len(payload)))
        uploaded = True
        result["upload"] = True
        stored = _step("audio_retrieval", lambda: get_private_audio_object(key))
        body = stored["Body"].read()
        try:
            stored["Body"].close()
        except Exception:
            pass
        result["retrieval"] = True
        result["checksum_match"] = hashlib.sha256(body).hexdigest() == digest
        if not result["checksum_match"]:
            raise StorageAcceptanceError("Retrieved audio checksum did not match.")
        _step("audio_unsigned_access", lambda: _unsigned_denied(cfg["endpoint_url"], cfg["region"], cfg["bucket"], key))
        result["unsigned_access_denied"] = True
    finally:
        if uploaded:
            _step("audio_deletion", lambda: delete_private_audio_object(key))
            try:
                client.head_object(Bucket=cfg["bucket"], Key=key)
            except ClientError as exc:
                if _status_code(exc) == 404 or exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                    result["deletion"] = True
                else:
                    raise StorageProbeStepError("audio_deletion_verify") from exc
            except Exception as exc:
                raise StorageProbeStepError("audio_deletion_verify") from exc
            else:
                raise StorageAcceptanceError("Synthetic audio object still exists after deletion.")
    return result


def _export_storage_config_diagnostics():
    """Report safe credential provenance for the export R2 client, never secret values."""
    def selected(primary, fallback):
        return primary if os.environ.get(primary, "").strip() else fallback if os.environ.get(fallback, "").strip() else None

    access_source = selected("DATA_EXPORT_AWS_ACCESS_KEY_ID", "R2_ACCESS_KEY_ID")
    secret_source = selected("DATA_EXPORT_AWS_SECRET_ACCESS_KEY", "R2_SECRET_ACCESS_KEY")
    endpoint_source = selected("DATA_EXPORT_AWS_ENDPOINT_URL_S3", "R2_ENDPOINT_URL")
    bucket_source = selected("DATA_EXPORT_STORAGE_BUCKET", "R2_BUCKET_NAME")
    region_source = selected("DATA_EXPORT_AWS_REGION", "R2_REGION")
    endpoint = os.environ.get(endpoint_source, "") if endpoint_source else ""
    host = endpoint.removeprefix("https://").split("/", 1)[0].split(":", 1)[0].lower()
    account_id = host[:-len(".r2.cloudflarestorage.com")] if host.endswith(".r2.cloudflarestorage.com") else None
    access_primary = os.environ.get("DATA_EXPORT_AWS_ACCESS_KEY_ID", "")
    access_alias = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_primary = os.environ.get("DATA_EXPORT_AWS_SECRET_ACCESS_KEY", "")
    secret_alias = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    region = os.environ.get(region_source, "") if region_source else ""
    if ".r2.cloudflarestorage.com" in endpoint.lower():
        region = "auto"
    return {
        "diagnostic_version": 2,
        "access_key_source": access_source,
        "access_key_id_suffix": os.environ.get(access_source, "")[-4:] if access_source else None,
        "secret_key_source": secret_source,
        "endpoint_source": endpoint_source,
        "bucket_source": bucket_source,
        "region_source": region_source,
        "credential_sources_mixed": bool(access_source and secret_source and
            access_source.startswith("DATA_EXPORT_") != secret_source.startswith("DATA_EXPORT_")),
        "dedicated_and_alias_keys_both_present": bool(access_primary and access_alias and secret_primary and secret_alias),
        "access_key_aliases_conflict": bool(access_primary and access_alias and access_primary != access_alias),
        "secret_key_aliases_conflict": bool(secret_primary and secret_alias and secret_primary != secret_alias),
        "endpoint_account_id": account_id,
        "endpoint_host": host or None,
        "bucket": os.environ.get(bucket_source, "") if bucket_source else None,
        "region": region or None,
    }


def run_private_storage_acceptance():
    """Probe the configured private audio bucket and R2 export bucket independently."""
    if os.environ.get("APP_ENV", "").strip().lower() != "staging":
        raise StorageAcceptanceError("Storage acceptance is staging-only.")

    key_suffix = uuid.uuid4().hex
    payload = _synthetic_wav()
    results = {}

    try:
        from audio_storage import storage_config, storage_config_diagnostics, _s3_client
        audio_configuration = storage_config_diagnostics()
        cfg = storage_config()
    except Exception as exc:
        results["audio"] = _safe_failure(exc, "audio_storage_configuration")
        results["audio"]["configured"] = False
        try:
            from audio_storage import storage_config_diagnostics
            results["audio"]["configuration"] = storage_config_diagnostics()
        except Exception:
            pass
    else:
        try:
            key = f"qa-acceptance/audio-{key_suffix}.wav"
            results["audio"] = _probe_audio(cfg, _s3_client(cfg), key, payload)
            results["audio"]["configuration"] = audio_configuration
        except Exception as exc:
            results["audio"] = _safe_failure(exc, getattr(exc, "failure_phase", "audio_storage_transfer"))
            # Keep non-secret configuration provenance even when the transfer fails.
            # Without this, the exact diagnostic needed to investigate rejected keys
            # disappears on the failure path.
            results["audio"]["configuration"] = audio_configuration

    # Canonical DATA_EXPORT_* settings are preferred. R2_* aliases support
    # existing Render deployments without ever reusing the separate audio bucket.
    required = {
        "access_key_id": os.environ.get("DATA_EXPORT_AWS_ACCESS_KEY_ID") or os.environ.get("R2_ACCESS_KEY_ID", ""),
        "secret_access_key": os.environ.get("DATA_EXPORT_AWS_SECRET_ACCESS_KEY") or os.environ.get("R2_SECRET_ACCESS_KEY", ""),
        "endpoint": os.environ.get("DATA_EXPORT_AWS_ENDPOINT_URL_S3") or os.environ.get("R2_ENDPOINT_URL", ""),
        "region": os.environ.get("DATA_EXPORT_AWS_REGION") or os.environ.get("R2_REGION", "auto"),
        "bucket": os.environ.get("DATA_EXPORT_STORAGE_BUCKET") or os.environ.get("R2_BUCKET_NAME", ""),
    }
    if ".r2.cloudflarestorage.com" in required["endpoint"]:
        required["region"] = "auto"
    missing = [
        f"{canonical} or {alias}"
        for key, canonical, alias in (
            ("access_key_id", "DATA_EXPORT_AWS_ACCESS_KEY_ID", "R2_ACCESS_KEY_ID"),
            ("secret_access_key", "DATA_EXPORT_AWS_SECRET_ACCESS_KEY", "R2_SECRET_ACCESS_KEY"),
            ("endpoint", "DATA_EXPORT_AWS_ENDPOINT_URL_S3", "R2_ENDPOINT_URL"),
            ("bucket", "DATA_EXPORT_STORAGE_BUCKET", "R2_BUCKET_NAME"),
        )
        if not required[key].strip()
    ]
    if missing:
        results["r2_exports"] = {
            "configured": False, "passed": False,
            "failure_phase": "r2_storage_configuration",
            "failure_class": "StorageAcceptanceError",
            "missing_settings": missing,
        }
    elif not required["endpoint"].startswith("https://"):
        results["r2_exports"] = {
            "configured": False, "passed": False,
            "failure_phase": "r2_storage_configuration",
            "failure_class": "StorageAcceptanceError",
            "configuration_issue": "endpoint_must_use_https",
        }
    else:
        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=required["endpoint"],
                region_name=required["region"],
                aws_access_key_id=required["access_key_id"],
                aws_secret_access_key=required["secret_access_key"],
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        except Exception as exc:
            results["r2_exports"] = _safe_failure(exc, "r2_client_initialization")
        else:
            try:
                key = f"qa-acceptance/export-{key_suffix}.wav"
                results["r2_exports"] = _probe_s3(
                    client, required["endpoint"], required["region"], required["bucket"], key, payload
                )
            except Exception as exc:
                results["r2_exports"] = _safe_failure(exc, getattr(exc, "failure_phase", "r2_storage_transfer"))

    if "audio" in results and "configuration" in results["audio"]:
        results["audio"]["configuration"]["diagnostic_version"] = 2
    if "r2_exports" in results:
        results["r2_exports"]["configuration"] = _export_storage_config_diagnostics()

    for value in results.values():
        value["passed"] = all(
            value.get(field) is True
            for field in ("upload", "retrieval", "checksum_match", "unsigned_access_denied", "deletion")
        )
    return {
        "passed": all(value.get("passed") is True for value in results.values()),
        "results": results,
    }
