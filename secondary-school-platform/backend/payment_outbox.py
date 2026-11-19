"""Durable owner-payment-alert outbox worker.

Run as a scheduled/background process, never inside the webhook request. Rows
are claimed with SKIP LOCKED, sent through the SMTP adapter, and retried with
bounded exponential backoff. Provider errors are not copied into the database.
"""
from payment_notifications import send_owner_payment_alert


MAX_ATTEMPTS = 8


def retry_delay_seconds(attempts):
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("Attempt count must be a positive integer")
    return min(3600, 30 * (2 ** min(attempts - 1, 7)))


def process_one_outbox_item():
    from database import connection

    with connection() as conn:
        row = conn.execute(
            """
            WITH candidate AS (
                SELECT id
                FROM payment_notification_outbox
                WHERE (
                    status IN ('queued','retry') AND available_at <= now()
                ) OR (
                    status='processing' AND locked_at < now() - interval '5 minutes'
                )
                ORDER BY available_at, created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            )
            UPDATE payment_notification_outbox AS o
            SET status='processing', attempts=o.attempts+1,
                locked_at=now(), updated_at=now()
            FROM candidate
            WHERE o.id=candidate.id
            RETURNING o.id, o.payload, o.attempts
            """
        ).fetchone()

    if not row:
        return {"status": "empty"}

    try:
        send_owner_payment_alert(row["payload"])
    except Exception:
        attempts = row["attempts"]
        with connection() as conn:
            if attempts >= MAX_ATTEMPTS:
                conn.execute(
                    """
                    UPDATE payment_notification_outbox
                    SET status='dead_letter', locked_at=NULL,
                        last_error_code='delivery_failed', updated_at=now()
                    WHERE id=%s AND status='processing'
                    """,
                    (row["id"],),
                )
                return {"status": "dead_letter", "attempts": attempts}
            conn.execute(
                """
                UPDATE payment_notification_outbox
                SET status='retry', locked_at=NULL,
                    available_at=now() + (%s * interval '1 second'),
                    last_error_code='delivery_failed', updated_at=now()
                WHERE id=%s AND status='processing'
                """,
                (retry_delay_seconds(attempts), row["id"]),
            )
        return {"status": "retry", "attempts": attempts}

    with connection() as conn:
        conn.execute(
            """
            UPDATE payment_notification_outbox
            SET status='sent', locked_at=NULL, sent_at=now(),
                last_error_code=NULL, updated_at=now()
            WHERE id=%s AND status='processing'
            """,
            (row["id"],),
        )
    return {"status": "sent", "attempts": row["attempts"]}
