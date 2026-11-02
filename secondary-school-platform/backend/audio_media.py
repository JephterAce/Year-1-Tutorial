"""Short-lived authorisation tokens for private lesson audio objects."""
import base64, hashlib, hmac, json, os, time
from pathlib import Path

class AudioAccessError(ValueError): pass

def _secret():
    value=os.environ.get("AUDIO_SIGNING_SECRET","")
    if len(value)<32: raise AudioAccessError("Audio signing is not configured.")
    return value.encode()

def issue_audio_token(student_id, topic_id, object_key, entitled, now=None, ttl=300):
    if not entitled: raise AudioAccessError("A current lesson entitlement is required.")
    if not all(isinstance(x,str) and x.strip() for x in (student_id,topic_id,object_key)):
        raise AudioAccessError("Invalid audio resource.")
    if object_key.startswith("/") or ".." in object_key.split("/") or chr(92) in object_key:
        raise AudioAccessError("Invalid private object key.")
    if isinstance(ttl,bool) or not isinstance(ttl,int) or not 30<=ttl<=600:
        raise AudioAccessError("Audio token lifetime must be 30–600 seconds.")
    now=int(time.time() if now is None else now)
    payload={"sub":student_id,"topic":topic_id,"key":object_key,"iat":now,
             "exp":now+ttl,"aud":"learnwise-private-audio"}
    encoded=base64.urlsafe_b64encode(json.dumps(payload,separators=(",",":"),sort_keys=True).encode()).rstrip(b"=").decode()
    sig=hmac.new(_secret(),encoded.encode(),hashlib.sha256).digest()
    return encoded+"."+base64.urlsafe_b64encode(sig).rstrip(b"=").decode()

def verify_audio_token(token, now=None):
    try:
        encoded,supplied=token.split(".",1)
        expected=hmac.new(_secret(),encoded.encode(),hashlib.sha256).digest()
        actual=base64.urlsafe_b64decode((supplied+"="*(-len(supplied)%4)).encode())
        if not hmac.compare_digest(expected,actual): raise AudioAccessError("Invalid audio token.")
        payload=json.loads(base64.urlsafe_b64decode((encoded+"="*(-len(encoded)%4)).encode()))
        current=int(time.time() if now is None else now)
        if payload.get("aud")!="learnwise-private-audio" or payload.get("exp",0)<=current:
            raise AudioAccessError("Audio token expired or has invalid audience.")
        if payload.get("iat",current+1)>current or payload["exp"]-payload["iat"]>600:
            raise AudioAccessError("Invalid audio token lifetime.")
        return payload
    except AudioAccessError: raise
    except Exception: raise AudioAccessError("Invalid audio token.") from None


def resolve_private_audio_path(storage_root, object_key):
    """Resolve an object key beneath a private local media root; reject symlink/path escapes."""
    if not isinstance(storage_root, str) or not storage_root.strip():
        raise AudioAccessError("Private audio storage is not configured.")
    if not isinstance(object_key, str) or not object_key.strip():
        raise AudioAccessError("Invalid private object key.")
    root = Path(storage_root).resolve()
    candidate = (root / object_key).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise AudioAccessError("Audio object is outside the private storage root.") from None
    if not candidate.is_file():
        raise AudioAccessError("Audio object is unavailable.")
    return candidate
