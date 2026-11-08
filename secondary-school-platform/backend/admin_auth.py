"""Dedicated database-backed admin authentication; no public provisioning."""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

from database import connection
from identity_policy import hash_session_id, verify_password
from admin_policy import AdminPrincipal

ADMIN_SESSION_TTL_HOURS = 8


class AdminAuthError(Exception):
    pass


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rate_limit(email, limit=6, action="admin_login", window_minutes=15):
    pepper = os.environ.get("AUTH_RATE_LIMIT_PEPPER", "")
    if len(pepper) < 32:
        raise RuntimeError("AUTH_RATE_LIMIT_PEPPER must contain at least 32 characters")
    key = hmac.new(pepper.encode(), email.encode(), hashlib.sha256).hexdigest()
    with connection() as conn:
        row = conn.execute(
            """INSERT INTO auth_rate_limits(action_key,subject_hash,window_started_at,attempts)
               VALUES (%s,%s,now(),1)
               ON CONFLICT(action_key,subject_hash) DO UPDATE SET
                 window_started_at=CASE WHEN auth_rate_limits.window_started_at < now()-interval '15 minutes'
                   THEN now() ELSE auth_rate_limits.window_started_at END,
                 attempts=CASE WHEN auth_rate_limits.window_started_at < now()-interval '15 minutes'
                   THEN 1 ELSE auth_rate_limits.attempts+1 END,
                 blocked_until=CASE WHEN auth_rate_limits.window_started_at < now()-interval '15 minutes'
                   THEN NULL WHEN auth_rate_limits.attempts >= %s
                   THEN now()+(%s * interval '1 minute') ELSE auth_rate_limits.blocked_until END
               RETURNING attempts,blocked_until""", (action, key, window_minutes, window_minutes, window_minutes, limit, window_minutes)
        ).fetchone()
    if row["attempts"] > limit or (row["blocked_until"] and row["blocked_until"] > datetime.now(timezone.utc)):
        raise AdminAuthError("Email or password is incorrect.")


def login_admin(email, password):
    email = email.strip().lower() if isinstance(email, str) else ""
    if len(email) > 254 or not email or not isinstance(password, str):
        raise AdminAuthError("Email or password is incorrect.")
    _rate_limit(email)
    with connection() as conn:
        admin = conn.execute(
            """SELECT id,email,role,is_active,password_hash FROM admin_users
               WHERE lower(trim(email))=%s""", (email,)
        ).fetchone()
        if not admin or not verify_password(admin["password_hash"], password) or admin["is_active"] is not True:
            # Avoid leaking account existence. A malformed/missing hash fails closed.
            if not admin:
                verify_password("scrypt:32768:8:1$invalid$invalid", password)
            raise AdminAuthError("Email or password is incorrect.")
        session_id, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
        conn.execute(
            """UPDATE admin_sessions SET revoked_at=now()
               WHERE admin_user_id=%s AND revoked_at IS NULL""", (admin["id"],)
        )
        conn.execute(
            """INSERT INTO admin_sessions(admin_user_id,session_id_hash,csrf_token_hash,expires_at)
               VALUES (%s,%s,%s,now()+interval '8 hours')""",
            (admin["id"], hash_session_id(session_id), _digest(csrf))
        )
        conn.execute("UPDATE admin_users SET last_login_at=now() WHERE id=%s", (admin["id"],))
        return {"session_id": session_id, "csrf_token": csrf}


def authenticate_admin(session_id):
    if not isinstance(session_id, str) or not 32 <= len(session_id) <= 200:
        return None
    with connection() as conn:
        row = conn.execute(
            """SELECT a.id,a.email,a.role,a.is_active,s.csrf_token_hash,s.id AS session_row_id
               FROM admin_sessions s JOIN admin_users a ON a.id=s.admin_user_id
               WHERE s.session_id_hash=%s AND s.revoked_at IS NULL AND s.expires_at>now()
                 AND a.is_active=true""", (hash_session_id(session_id),)
        ).fetchone()
        if not row:
            return None
        conn.execute("UPDATE admin_sessions SET last_seen_at=now() WHERE id=%s", (row["session_row_id"],))
        return {"principal": AdminPrincipal(str(row["id"]), row["role"], row["is_active"]),
                "admin_id": str(row["id"]), "email": row["email"], "role": row["role"],
                "csrf_token_hash": row["csrf_token_hash"]}


def validate_admin_csrf(session, token):
    return bool(session and isinstance(token, str) and
                hmac.compare_digest(session["csrf_token_hash"], _digest(token)))


def logout_admin(session_id):
    if not isinstance(session_id, str) or not session_id:
        return
    with connection() as conn:
        conn.execute(
            "UPDATE admin_sessions SET revoked_at=now() WHERE session_id_hash=%s AND revoked_at IS NULL",
            (hash_session_id(session_id),)
        )


def record_admin_audit(admin_id, event_type, entity_type, entity_id, details=None):
    """Append a minimal audit event; callers must not pass secrets or student payloads."""
    if not all(isinstance(x, str) and x.strip() for x in (event_type, entity_type, entity_id)):
        raise ValueError("Audit event metadata is required")
    if details is not None and not isinstance(details, dict):
        raise ValueError("Audit details must be an object")
    from psycopg.types.json import Jsonb
    with connection() as conn:
        conn.execute(
            """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
               VALUES (%s,%s,%s,%s,%s)""",
            (admin_id, event_type[:100], entity_type[:100], entity_id[:200], Jsonb(details or {}))
        )


def reserve_admin_smtp_diagnostic(email):
    """Allow one staging SMTP diagnostic per admin per hour."""
    email = email.strip().lower() if isinstance(email, str) else ""
    if not email:
        raise AdminAuthError("Administrator email is unavailable.")
    _rate_limit(email, limit=1, action="admin_smtp_diagnostic", window_minutes=60)
