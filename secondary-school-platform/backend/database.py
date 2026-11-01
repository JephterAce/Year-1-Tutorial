"""Small PostgreSQL repository layer.

DATABASE_URL is supplied by the deployment environment and must never be committed.
The connection string should use TLS and a least-privilege application database role.
"""
import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


def database_url():
    return os.environ.get("DATABASE_URL")


@contextmanager
def connection():
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=5) as conn:
        yield conn


def database_ready():
    try:
        with connection() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def list_published_topics(class_level=None, subject_slug=None, term_number=None, search=None):
    clauses = ["t.status = 'published'"]
    params = []
    if class_level in ("SS1", "SS2", "SS3"):
        clauses.append("t.class_level = %s")
        params.append(class_level)
    if subject_slug:
        clauses.append("s.slug = %s")
        params.append(subject_slug)
    if term_number in (1, 2, 3):
        clauses.append("tr.term_number = %s")
        params.append(term_number)
    if search:
        clauses.append("(t.title ILIKE %s OR COALESCE(t.summary, '') ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    query = """
        SELECT t.id, t.class_level, s.slug AS subject_slug, s.name AS subject, s.offering_group,
               tr.term_number, tr.label AS term, t.slug, t.title, t.summary,
               t.learning_objectives, t.price_kobo, t.currency, t.estimated_minutes
        FROM topics t
        JOIN subjects s ON s.id = t.subject_id
        JOIN terms tr ON tr.id = t.term_id
        WHERE """ + " AND ".join(clauses) + """
        ORDER BY t.class_level, s.sort_order, tr.term_number, t.sort_order, t.title
        LIMIT 200
    """
    with connection() as conn:
        return conn.execute(query, params).fetchall()


def fulfil_verified_payment(reference, verified_transaction):
    """Atomically record a Paystack-verified payment, entitlement and email outbox item.

    Call only with the result of verify_paystack_transaction(), after the webhook
    signature and charge.success event have been authenticated. This function
    deliberately does not send email; a separate worker must claim/retry outbox rows.
    """
    import hashlib
    import json
    from psycopg.types.json import Jsonb

    if not isinstance(verified_transaction, dict):
        raise ValueError("A verified transaction is required")
    if (
        verified_transaction.get("reference") != reference
        or verified_transaction.get("status") != "success"
        or verified_transaction.get("currency") != "NGN"
        or isinstance(verified_transaction.get("amount_kobo"), bool)
        or not isinstance(verified_transaction.get("amount_kobo"), int)
        or verified_transaction["amount_kobo"] <= 0
    ):
        raise ValueError("Verified transaction does not match the expected payment")

    dedupe_key = "paystack:owner-alert:" + hashlib.sha256(reference.encode("utf-8")).hexdigest()
    event_id = "paystack:charge.success:" + hashlib.sha256(reference.encode("utf-8")).hexdigest()
    minimal_event = {
        "reference": reference,
        "amount": verified_transaction["amount_kobo"],
        "currency": "NGN",
        "status": "success",
    }

    with connection() as conn:
        payment = conn.execute(
            """
            SELECT p.id, p.student_id, p.topic_id, p.provider_reference,
                   p.amount_kobo, p.currency, p.status, t.title
            FROM payment_transactions p
            JOIN topics t ON t.id = p.topic_id
            WHERE p.provider = 'paystack' AND p.provider_reference = %s
            FOR UPDATE OF p
            """,
            (reference,),
        ).fetchone()
        if not payment:
            raise ValueError("No pending Learnwise order matches this payment reference")
        if (
            payment["amount_kobo"] != verified_transaction["amount_kobo"]
            or payment["currency"] != "NGN"
            or payment["provider_reference"] != verified_transaction["reference"]
        ):
            raise ValueError("Verified transaction does not match the Learnwise order")
        if payment["status"] not in ("initialized", "pending", "successful"):
            raise ValueError("Learnwise order is not eligible for fulfilment")

        conn.execute(
            """
            INSERT INTO payment_webhook_events(provider,event_id,event_type,payload,processed_at)
            VALUES ('paystack',%s,'charge.success',%s,now())
            ON CONFLICT (event_id) DO NOTHING
            """,
            (event_id, Jsonb(minimal_event)),
        )
        if payment["status"] != "successful":
            conn.execute(
                """
                UPDATE payment_transactions
                SET status='successful', verified_at=now(), provider_payload=%s
                WHERE id=%s
                """,
                (Jsonb(minimal_event), payment["id"]),
            )
        conn.execute(
            """
            INSERT INTO entitlements(student_id,topic_id,payment_id,grant_reason)
            VALUES (%s,%s,%s,'purchase')
            ON CONFLICT (student_id,topic_id,payment_id) DO NOTHING
            """,
            (payment["student_id"], payment["topic_id"], payment["id"]),
        )
        email_payload = {
            "reference": reference,
            "amount_major": verified_transaction["amount_kobo"] / 100,
            "currency": "NGN",
            "paid_at": verified_transaction.get("paid_at") or "Paystack-confirmed; timestamp unavailable",
            "product": payment["title"],
        }
        conn.execute(
            """
            INSERT INTO payment_notification_outbox
                (payment_id,event_type,dedupe_key,payload,status)
            VALUES (%s,'owner_payment_alert',%s,%s,'queued')
            ON CONFLICT (dedupe_key) DO NOTHING
            """,
            (payment["id"], dedupe_key, Jsonb(email_payload)),
        )
    return {"status": "successful", "reference": reference, "notification": "queued"}


def get_pending_paystack_order(reference):
    """Return the expected amount for a server-created Learnwise payment reference."""
    with connection() as conn:
        row = conn.execute(
            """
            SELECT provider_reference, amount_kobo, currency, status
            FROM payment_transactions
            WHERE provider='paystack' AND provider_reference=%s
            """,
            (reference,),
        ).fetchone()
    if not row or row["status"] not in ("initialized", "pending", "successful"):
        raise ValueError("No eligible Learnwise order matches this payment reference")
    if row["currency"] != "NGN" or row["amount_kobo"] <= 0:
        raise ValueError("Learnwise order has invalid payment terms")
    return {"reference": row["provider_reference"], "amount_kobo": row["amount_kobo"]}
