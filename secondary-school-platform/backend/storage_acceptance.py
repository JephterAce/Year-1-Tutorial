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
        operation = getattr(cause, "operation_name", None)
        if isinstance(operation, str) and re.fullmatch(r"[A-Za-z0-9]{1,48}", operation):
            error["provider_operation"] = operation
        request_id = metadata.get("RequestId") or metadata.get("HostId")
        if isinstance(request_id, str) and re.fullmatch(r"[A-Za-z0-9+/=_-]{1,96}", request_id):
            error["provider_request_id"] = request_id
        message = details.get("Message") if isinstance(details, dict) else None
        if isinstance(message, str):
            # Keep the provider's useful error explanation while stripping URLs
            # and long token-like values. Never expose raw SDK exceptions.
            safe_message = re.sub(r"https?://\S+", "[url]", message)
            safe_message = re.sub(r"\b[A-Za-z0-9_+/=-]{24,}\b", "[redacted]", safe_message)
            safe_message = re.sub(r"[^A-Za-z0-9 .,;:_()'\-]", "", safe_message)
            safe_message = safe_message.strip()[:180]
            if safe_message:
                error["provider_message"] = safe_message
    if type(cause).__name__ in {"EndpointConnectionError", "ConnectTimeoutError", "ReadTimeoutError", "TimeoutError"}:
        error["retryable"] = True
    return error

def _unsigned_http_denied(endpoint, bucket, key):
    """Check R2 anonymous access with a bare HTTPS GET, independent of SDK signing."""
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.request import Request, urlopen
    import xml.etree.ElementTree as ET

    url = f"{endpoint.rstrip('/')}/{quote(bucket, safe='')}/{quote(key, safe='/')}"
    request = Request(url, headers={"Accept": "application/xml"}, method="GET")

    def raise_provider_error(status, headers, body):
        values = {}
        try:
            root = ET.fromstring(body[:4096])
            for node in root.iter():
                name = node.tag.rsplit("}", 1)[-1]
                if name in {"Code", "Message", "RequestId", "HostId"} and node.text:
                    values[name] = node.text.strip()
        except Exception:
            pass
        request_id = headers.get("x-amz-request-id") or values.get("RequestId")
        host_id = headers.get("x-amz-id-2") or values.get("HostId")
        metadata = {"HTTPStatusCode": status, "HTTPHeaders": {}, "RetryAttempts": 0}
        if request_id:
            metadata["RequestId"] = request_id
        if host_id:
            metadata["HostId"] = host_id
        response = {
            "Error": {
                "Code": values.get("Code") or "HTTPError",
                "Message": values.get("Message") or f"Anonymous GetObject returned HTTP {status}.",
            },
            "ResponseMetadata": metadata,
        }
        raise ClientError(response, "GetObject")

    try:
        response = urlopen(request, timeout=20)
    except HTTPError as exc:
        try:
            body = exc.read(4096)
        finally:
            exc.close()
        if exc.code in (401, 403):
            return True
        # Do not chain the HTTPError: the synthetic ClientError carries the
        # bounded S3 response metadata consumed by _safe_failure.
        raise_provider_error(exc.code, exc.headers or {}, body)

    with response:
        status = getattr(response, "status", response.getcode())
        if status in (401, 403):
            return True
        if 200 <= status < 300:
            # Read only a small amount before closing; the QA object is synthetic.
            response.read(512)
            raise StorageAcceptanceError("Private R2 object was readable without credentials.")
        body = response.read(4096)
        raise_provider_error(status, response.headers or {}, body)


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
        _step("r2_unsigned_access", lambda: _unsigned_http_denied(endpoint, bucket, key))
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
