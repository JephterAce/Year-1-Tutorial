"""Optional in-process worker that drains the payment notification outbox.

Off unless PAYMENT_OUTBOX_WORKER_ENABLED is true. It sends nothing until the SMTP
settings exist, so queued alerts are never burned as failed attempts while email
is unconfigured. Rows are claimed with SKIP LOCKED, so several gunicorn workers
can each run one of these threads safely.
"""
import logging
import os
import threading
import time

log = logging.getLogger(__name__)
_lock = threading.Lock()
_thread = None
POLL_SECONDS = 30
IDLE_SECONDS = 60


def worker_enabled():
    return os.environ.get("PAYMENT_OUTBOX_WORKER_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}


def smtp_ready():
    return all(os.environ.get(name, "").strip() for name in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"))


def run_once():
    """Process at most one queued item. Returns a short status string."""
    if not os.environ.get("DATABASE_URL", "").strip():
        return "no_database"
    if not smtp_ready():
        return "smtp_not_configured"
    from payment_outbox import process_one_outbox_item
    return process_one_outbox_item().get("status", "unknown")


def _loop():
    warned = False
    while True:
        try:
            status = run_once()
            if status == "smtp_not_configured" and not warned:
                log.warning("Payment outbox worker is idle: SMTP settings are not configured")
                warned = True
            if status != "smtp_not_configured":
                warned = False
            delay = 1 if status == "sent" else (POLL_SECONDS if status == "empty" else IDLE_SECONDS)
        except Exception:
            log.error("Payment outbox worker iteration failed")
            delay = IDLE_SECONDS
        time.sleep(delay)


def start_outbox_worker():
    """Start the daemon thread once per process. Returns True if a thread was started."""
    global _thread
    if not worker_enabled():
        return False
    with _lock:
        if _thread is not None:
            return False
        _thread = threading.Thread(target=_loop, name="payment-outbox-worker", daemon=True)
        _thread.start()
    return True
