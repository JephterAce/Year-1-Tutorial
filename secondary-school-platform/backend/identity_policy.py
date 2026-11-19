"""Identity security primitives for the Learnwise backend.

These helpers do not create accounts or sessions by themselves. Database-backed
registration, rate limiting, email delivery and cookie/session routes must call
them only after the corresponding service and migrations are implemented.
"""
import hashlib
import re
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def normalise_email(value):
    if not isinstance(value, str):
        raise ValueError("A valid email address is required.")
    email = value.strip().lower()
    if len(email) > 254 or email.count("@") != 1:
        raise ValueError("A valid email address is required.")
    local, domain = email.rsplit("@", 1)
    if not local or not domain or "." not in domain or any(ch.isspace() for ch in email):
        raise ValueError("A valid email address is required.")
    return email


def validate_username(value):
    if not isinstance(value, str) or not USERNAME_PATTERN.fullmatch(value):
        raise ValueError("Username must be 3–24 characters using letters, numbers or underscores.")
    return value.lower()


def hash_password(password):
    if not isinstance(password, str) or not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters.")
    # Werkzeug's scrypt hash embeds its parameters and a random salt.
    return generate_password_hash(password, method="scrypt")


def verify_password(password_hash, password):
    if not isinstance(password_hash, str) or not isinstance(password, str):
        return False
    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return False


def create_one_time_token():
    """Return a high-entropy raw token and its SHA-256 storage digest."""
    raw_token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, digest


def hash_session_id(session_id):
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Session identifier is required.")
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()
