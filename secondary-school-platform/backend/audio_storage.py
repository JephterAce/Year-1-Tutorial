"""Private S3-compatible object retrieval for branch-scoped Neon storage."""
import os
import re

class AudioStorageError(RuntimeError):
    pass

def validate_object_key(object_key):
    if not isinstance(object_key, str) or not object_key.strip():
        raise AudioStorageError("Invalid private audio object key.")
    if object_key.startswith("/") or "\\" in object_key or "\x00" in object_key:
        raise AudioStorageError("Invalid private audio object key.")
    if any(part in ("", ".", "..") for part in object_key.split("/")):
        raise AudioStorageError("Invalid private audio object key.")
    return object_key

def storage_config():
    required = {
        "access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "endpoint_url": os.environ.get("AWS_ENDPOINT_URL_S3", ""),
        "region": os.environ.get("AWS_REGION", ""),
        "bucket": os.environ.get("AUDIO_STORAGE_BUCKET", ""),
    }
    if not all(isinstance(v, str) and v.strip() for v in required.values()):
        raise AudioStorageError("Private object storage is not configured.")
    if not required["endpoint_url"].startswith("https://"):
        raise AudioStorageError("Private object storage endpoint must use HTTPS.")
    return required

def _s3_client(cfg):
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=cfg["endpoint_url"],
        region_name=cfg["region"],
        aws_access_key_id=cfg["access_key_id"],
        aws_secret_access_key=cfg["secret_access_key"],
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

def put_private_audio_object(object_key, fileobj, content_type, content_length):
    key = validate_object_key(object_key)
    if content_type not in {"audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg", "audio/webm"}:
        raise AudioStorageError("Unsupported audio content type.")
    if isinstance(content_length, bool) or not isinstance(content_length, int) or not 1 <= content_length <= 100 * 1024 * 1024:
        raise AudioStorageError("Audio file must be between 1 byte and 100 MB.")
    try:
        cfg = storage_config()
        client = _s3_client(cfg)
        result = client.put_object(
            Bucket=cfg["bucket"], Key=key, Body=fileobj,
            ContentType=content_type, ContentLength=content_length,
            Metadata={"learnwise-review-status": "pending"},
        )
        return result.get("ETag", "").strip('"')
    except AudioStorageError:
        raise
    except Exception as exc:
        raise AudioStorageError("Private audio upload failed.") from exc

def delete_private_audio_object(object_key):
    key = validate_object_key(object_key)
    try:
        cfg = storage_config()
        _s3_client(cfg).delete_object(Bucket=cfg["bucket"], Key=key)
    except AudioStorageError:
        raise
    except Exception as exc:
        raise AudioStorageError("Private audio cleanup failed.") from exc

def get_private_audio_object(object_key, range_header=None):
    key = validate_object_key(object_key)
    cfg = storage_config()
    try:
        params = {"Bucket": cfg["bucket"], "Key": key}
        if range_header:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
            if not match or (not match.group(1) and not match.group(2)):
                raise AudioStorageError("Invalid audio byte range.")
            start, end = match.groups()
            if (start and end and int(start) > int(end)) or (not start and end == "0"):
                raise AudioStorageError("Invalid audio byte range.")
            params["Range"] = range_header.strip()
        return _s3_client(cfg).get_object(**params)
    except AudioStorageError:
        raise
    except Exception as exc:
        raise AudioStorageError("Private audio object is unavailable.") from exc
