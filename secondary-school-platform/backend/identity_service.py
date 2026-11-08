"""Database-backed student identity service.

Raw verification/reset tokens and session identifiers are returned only to the
caller for delivery/cookie issuance. Only SHA-256 digests are persisted.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from identity_policy import (
    create_one_time_token, hash_password, hash_session_id,
    normalise_email, validate_username, verify_password,
)
from database import connection

SESSION_COOKIE = "learnwise_session"
SESSION_TTL = timedelta(hours=12)
VERIFY_TTL = timedelta(hours=24)
RESET_TTL = timedelta(minutes=30)
RATE_WINDOW = timedelta(minutes=15)


class IdentityError(Exception):
    pass


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rate_limit(action, subject, limit=8):
    """Atomic fixed-window limit keyed by an HMAC of the supplied subject."""
    pepper = os.environ.get("AUTH_RATE_LIMIT_PEPPER", "")
    if len(pepper) < 32:
        raise RuntimeError("AUTH_RATE_LIMIT_PEPPER must contain at least 32 characters")
    key = hmac.new(pepper.encode(), subject.encode(), hashlib.sha256).hexdigest()
    with connection() as limiter_conn:
        row = limiter_conn.execute(
        """INSERT INTO auth_rate_limits(action_key,subject_hash,window_started_at,attempts)
           VALUES (%s,%s,now(),1)
           ON CONFLICT(action_key,subject_hash) DO UPDATE SET
             window_started_at=CASE
               WHEN auth_rate_limits.window_started_at < now() - interval '15 minutes'
               THEN now() ELSE auth_rate_limits.window_started_at END,
             attempts=CASE
               WHEN auth_rate_limits.window_started_at < now() - interval '15 minutes'
               THEN 1 ELSE auth_rate_limits.attempts + 1 END,
             blocked_until=CASE
               WHEN auth_rate_limits.window_started_at < now() - interval '15 minutes'
               THEN NULL
               WHEN auth_rate_limits.attempts >= %s
               THEN now() + interval '15 minutes'
               ELSE auth_rate_limits.blocked_until END
           RETURNING attempts,blocked_until""",
        (action, key, limit),
    ).fetchone()
    if row["blocked_until"] and row["blocked_until"] > datetime.now(timezone.utc):
        raise IdentityError("Please wait before trying again.")
    if row["attempts"] > limit:
        raise IdentityError("Please wait before trying again.")


def register_student(email, username, display_name, class_level, password):
    email = normalise_email(email)
    username = validate_username(username)
    display_name = " ".join(str(display_name or "").split())
    if not 2 <= len(display_name) <= 80:
        raise ValueError("Display name must be between 2 and 80 characters.")
    if class_level not in ("SS1", "SS2", "SS3"):
        raise ValueError("Choose SS1, SS2 or SS3.")
    password_hash = hash_password(password)
    raw_token, token_hash = create_one_time_token()
    with connection() as conn:
        _rate_limit("register", email, limit=5)
        try:
            student = conn.execute(
                """INSERT INTO students(email,username,display_name,class_level,password_hash,
                       account_status,profile_visibility,marketing_opt_in)
                   VALUES (%s,%s,%s,%s,%s,'pending','private',false)
                   RETURNING id,email,username,display_name,class_level""",
                (email, username, display_name, class_level, password_hash),
            ).fetchone()
        except Exception as exc:
            # Do not leak which identifier already exists.
            if getattr(exc, "sqlstate", None) == "23505":
                raise IdentityError("We could not create that account. Check your details or sign in.") from None
            raise
        conn.execute(
            """INSERT INTO identity_tokens(student_id,purpose,token_hash,expires_at)
               VALUES (%s,'verify_email',%s,now() + interval '24 hours')""",
            (student["id"], token_hash),
        )
        conn.execute(
            """INSERT INTO student_consent_records(student_id,consent_type,policy_version,granted)
               VALUES (%s,'privacy_notice',%s,true),(%s,'terms_of_service',%s,true)""",
            (student["id"], os.environ.get("PRIVACY_NOTICE_VERSION", "draft-1"),
             student["id"], os.environ.get("TERMS_VERSION", "draft-1")),
        )
    return {"student": dict(student), "verification_token": raw_token}


def verify_student_email(raw_token):
    if not isinstance(raw_token, str) or not 32 <= len(raw_token) <= 200:
        raise IdentityError("This verification link is invalid or has expired.")
    token_hash = _digest(raw_token)
    with connection() as conn:
        token = conn.execute(
            """SELECT t.id,t.student_id,t.purpose,s.is_synthetic_qa,s.synthetic_qa_expires_at
               FROM identity_tokens t JOIN students s ON s.id=t.student_id
               WHERE t.token_hash=%s
                 AND t.purpose IN ('verify_email','verify_qa_email')
                 AND t.consumed_at IS NULL AND t.expires_at > now()
                 AND ((t.purpose='verify_email' AND s.is_synthetic_qa=false)
                   OR (t.purpose='verify_qa_email' AND s.is_synthetic_qa=true
                       AND s.synthetic_qa_expires_at > now()))
               FOR UPDATE OF t,s""", (token_hash,)
        ).fetchone()
        if not token:
            raise IdentityError("This verification link is invalid or has expired.")
        conn.execute("UPDATE identity_tokens SET consumed_at=now() WHERE id=%s", (token["id"],))
        conn.execute(
            """UPDATE students SET email_verified_at=now(),account_status='active',updated_at=now()
               WHERE id=%s AND account_status='pending'""", (token["student_id"],)
        )
    return True


def login_student(email, password):
    try:
        email = normalise_email(email)
    except ValueError:
        email = "invalid"
    with connection() as conn:
        _rate_limit("login", email, limit=8)
        student = conn.execute(
            """SELECT id,password_hash,account_status FROM students
               WHERE lower(email)=%s
                 AND (is_synthetic_qa=false OR synthetic_qa_expires_at > now())""", (email,)
        ).fetchone()
        # Constant-work fallback reduces account-enumeration timing differences.
        if not student:
            verify_password("scrypt:32768:8:1$invalid$invalid", password or "")
            raise IdentityError("Email or password is incorrect.")
        if not verify_password(student["password_hash"], password):
            raise IdentityError("Email or password is incorrect.")
        if student["account_status"] != "active":
            raise IdentityError("Email or password is incorrect.")
        session_id = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        conn.execute(
            """UPDATE student_sessions SET revoked_at=now()
               WHERE student_id=%s AND revoked_at IS NULL""", (student["id"],)
        )
        conn.execute(
            """INSERT INTO student_sessions(student_id,session_id_hash,csrf_token_hash,expires_at)
               VALUES (%s,%s,%s,now() + interval '12 hours')""",
            (student["id"], hash_session_id(session_id), _digest(csrf_token)),
        )
        conn.execute("UPDATE students SET last_login_at=now() WHERE id=%s", (student["id"],))
        return {"session_id": session_id, "csrf_token": csrf_token, "student_id": str(student["id"])}


def authenticate_session(session_id):
    if not isinstance(session_id, str) or not 32 <= len(session_id) <= 200:
        return None
    with connection() as conn:
        row = conn.execute(
            """SELECT s.id AS student_id,s.email,s.username,s.display_name,s.class_level,
                      s.is_synthetic_qa,s.synthetic_qa_expires_at,
                      ss.csrf_token_hash,ss.id AS session_row_id
               FROM student_sessions ss JOIN students s ON s.id=ss.student_id
               WHERE ss.session_id_hash=%s AND ss.revoked_at IS NULL
                 AND ss.expires_at > now() AND s.account_status='active'
                 AND s.email_verified_at IS NOT NULL
                 AND (s.is_synthetic_qa=false OR s.synthetic_qa_expires_at > now())""",
            (hash_session_id(session_id),),
        ).fetchone()
        if row:
            conn.execute("UPDATE student_sessions SET last_seen_at=now() WHERE id=%s",
                         (row["session_row_id"],))
        return dict(row) if row else None


def validate_csrf(session, csrf_token):
    return bool(
        session and isinstance(csrf_token, str) and
        hmac.compare_digest(session["csrf_token_hash"], _digest(csrf_token))
    )


def logout_student(session_id):
    if not isinstance(session_id, str) or not session_id:
        return
    with connection() as conn:
        conn.execute(
            "UPDATE student_sessions SET revoked_at=now() WHERE session_id_hash=%s AND revoked_at IS NULL",
            (hash_session_id(session_id),),
        )


def request_password_reset(email):
    try:
        email = normalise_email(email)
    except ValueError:
        email = "invalid"
    raw_token = None
    with connection() as conn:
        _rate_limit("password_reset", email, limit=5)
        student = conn.execute(
            "SELECT id FROM students WHERE lower(email)=%s AND account_status='active'",
            (email,),
        ).fetchone()
        if student:
            raw_token, token_hash = create_one_time_token()
            conn.execute(
                """UPDATE identity_tokens SET consumed_at=now()
                   WHERE student_id=%s AND purpose='reset_student_password' AND consumed_at IS NULL""",
                (student["id"],),
            )
            conn.execute(
                """INSERT INTO identity_tokens(student_id,purpose,token_hash,expires_at)
                   VALUES (%s,'reset_student_password',%s,now() + interval '30 minutes')""",
                (student["id"], token_hash),
            )
    # Caller always returns the same public response; only deliver if token exists.
    return raw_token


def reset_student_password(raw_token, new_password):
    password_hash = hash_password(new_password)
    if not isinstance(raw_token, str) or not 32 <= len(raw_token) <= 200:
        raise IdentityError("This reset link is invalid or has expired.")
    with connection() as conn:
        token = conn.execute(
            """SELECT id,student_id FROM identity_tokens
               WHERE token_hash=%s AND purpose='reset_student_password'
                 AND consumed_at IS NULL AND expires_at > now() FOR UPDATE""",
            (_digest(raw_token),),
        ).fetchone()
        if not token:
            raise IdentityError("This reset link is invalid or has expired.")
        conn.execute("UPDATE identity_tokens SET consumed_at=now() WHERE id=%s", (token["id"],))
        conn.execute("UPDATE students SET password_hash=%s,updated_at=now() WHERE id=%s",
                     (password_hash, token["student_id"]))
        conn.execute("UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",
                     (token["student_id"],))
    return True



def provision_synthetic_qa_student():
    """Create one short-lived synthetic identity without writing consent records."""
    if (
        os.environ.get("APP_ENV", "").strip().lower() != "staging"
        or os.environ.get("STAGING_QA_IDENTITY_ENABLED", "").strip().lower() not in {"1", "true", "yes", "on"}
        or os.environ.get("STUDENT_REGISTRATION_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}
    ):
        raise IdentityError("Synthetic QA provisioning is unavailable.")
    email = normalise_email(os.environ.get("STAGING_QA_EMAIL", ""))
    username = "qa_" + secrets.token_hex(8)
    temporary_password = secrets.token_urlsafe(24)
    password_hash = hash_password(temporary_password)
    raw_token, token_hash = create_one_time_token()
    with connection() as conn:
        _rate_limit("synthetic_qa_provision", email, limit=1)
        try:
            student = conn.execute(
                """INSERT INTO students(
                       email,username,display_name,class_level,password_hash,
                       account_status,profile_visibility,marketing_opt_in,
                       is_synthetic_qa,synthetic_qa_expires_at
                   )
                   VALUES (%s,%s,'Synthetic QA Student','SS1',%s,
                           'pending','private',false,true,now()+interval '24 hours')
                   RETURNING id,email,username,display_name,class_level,synthetic_qa_expires_at""",
                (email, username, password_hash),
            ).fetchone()
        except Exception as exc:
            if getattr(exc, "sqlstate", None) == "23505":
                raise IdentityError("A synthetic QA identity already exists or the configured mailbox is in use.") from None
            raise
        conn.execute(
            """INSERT INTO identity_tokens(student_id,purpose,token_hash,expires_at)
               VALUES (%s,'verify_qa_email',%s,now()+interval '30 minutes')""",
            (student["id"], token_hash),
        )
    return {
        "student": dict(student),
        "verification_token": raw_token,
        "temporary_password": temporary_password,
    }


def revoke_synthetic_qa_student(student_id):
    """Revoke an explicitly marked QA identity and all its sessions/tokens."""
    with connection() as conn:
        student = conn.execute(
            """SELECT id FROM students
               WHERE id=%s AND is_synthetic_qa=true
               FOR UPDATE""",
            (student_id,),
        ).fetchone()
        if not student:
            raise IdentityError("Synthetic QA identity was not found.")
        conn.execute(
            "UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",
            (student_id,),
        )
        conn.execute(
            "UPDATE identity_tokens SET consumed_at=now() WHERE student_id=%s AND consumed_at IS NULL",
            (student_id,),
        )
        conn.execute(
            """UPDATE students SET account_status='closed',email=NULL,email_verified_at=NULL,
                      updated_at=now()
               WHERE id=%s AND is_synthetic_qa=true""",
            (student_id,),
        )
    return True


def expire_synthetic_qa_students():
    """Close expired QA identities and revoke all associated credentials."""
    with connection() as conn:
        rows = conn.execute(
            """SELECT id FROM students
               WHERE is_synthetic_qa=true AND synthetic_qa_expires_at<=now()
                 AND account_status IN ('pending','active')
               FOR UPDATE"""
        ).fetchall()
        ids = [row["id"] for row in rows]
        if not ids:
            return 0
        conn.execute(
            "UPDATE student_sessions SET revoked_at=now() WHERE student_id=ANY(%s) AND revoked_at IS NULL",
            (ids,),
        )
        conn.execute(
            "UPDATE identity_tokens SET consumed_at=now() WHERE student_id=ANY(%s) AND consumed_at IS NULL",
            (ids,),
        )
        conn.execute(
            """UPDATE students SET account_status='closed',email=NULL,email_verified_at=NULL,
                      updated_at=now()
               WHERE id=ANY(%s) AND is_synthetic_qa=true""",
            (ids,),
        )
    return len(ids)
