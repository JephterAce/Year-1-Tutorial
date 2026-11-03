"""Private S3-compatible object retrieval for branch-scoped Neon storage."""
import os

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

def get_private_audio_object(object_key, range_header=None):
    key = validate_object_key(object_key)
    cfg = storage_config()
    try:
        import boto3
        from botocore.config import Config
        client = boto3.client(
            "s3",
            endpoint_url=cfg["endpoint_url"],
            region_name=cfg["region"],
            aws_access_key_id=cfg["access_key_id"],
            aws_secret_access_key=cfg["secret_access_key"],
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        params = {"Bucket": cfg["bucket"], "Key": key}
        if range_header:
            if not range_header.startswith("bytes=") or "," in range_header:
                raise AudioStorageError("Invalid audio byte range.")
            params["Range"] = range_header
        result = client.get_object(**params)
        return result
    except AudioStorageError:
        raise
    except Exception as exc:
        raise AudioStorageError("Private audio object is unavailable.") from exc
