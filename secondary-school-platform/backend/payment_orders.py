"""Server-priced Paystack checkout initialisation; never accepts a client-supplied amount."""
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from uuid import uuid4

from database import connection


class PaymentOrderError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def _initialise_with_paystack(email, reference, amount_kobo, callback_url, secret, opener=urlopen):
    payload = {
        "email": email,
        "amount": amount_kobo,
        "currency": "NGN",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": {"platform": "learnwise", "order_reference": reference},
    }
    request = Request(
        "https://api.paystack.co/transaction/initialize",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + secret, "Content-Type": "application/json",
                 "Accept": "application/json"},
        method="POST",
    )
    try:
        with opener(request, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PaymentOrderError("provider_unavailable", "Checkout is temporarily unavailable.", 503) from exc
    data = result.get("data") if isinstance(result, dict) else None
    if result.get("status") is not True or not isinstance(data, dict):
        raise PaymentOrderError("provider_rejected", "Checkout could not be initialised.", 503)
    if data.get("reference") != reference or not isinstance(data.get("authorization_url"), str):
        raise PaymentOrderError("provider_response_invalid", "Checkout provider response was invalid.", 503)
    checkout_url = urlsplit(data["authorization_url"])
    if checkout_url.scheme != "https" or checkout_url.hostname != "checkout.paystack.com":
        raise PaymentOrderError("provider_response_invalid", "Checkout provider response was invalid.", 503)
    return {"authorization_url": data["authorization_url"], "access_code": data.get("access_code")}


def create_topic_checkout(student_id, topic_id, opener=urlopen):
    secret = os.environ.get("PAYSTACK_SECRET_KEY", "").strip()
    base_url = os.environ.get("PUBLIC_APP_URL", "").strip().rstrip("/")
    if not secret or not base_url.startswith("https://"):
        raise PaymentOrderError("checkout_not_configured", "Secure checkout is not configured.", 503)
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", str(topic_id)):
        raise PaymentOrderError("invalid_topic", "Choose a valid lesson.", 400)
    reference = "lw_" + uuid4().hex
    with connection() as conn:
        student = conn.execute(
            """SELECT email FROM students
               WHERE id=%s AND account_status='active' AND email_verified_at IS NOT NULL
               FOR SHARE""", (student_id,)
        ).fetchone()
        if not student:
            raise PaymentOrderError("account_not_ready", "Verify your account before purchasing.", 403)
        topic = conn.execute(
            """SELECT id,title,price_kobo,currency FROM topics
               WHERE id=%s AND status='published' FOR SHARE""", (topic_id,)
        ).fetchone()
        if not topic:
            raise PaymentOrderError("topic_unavailable", "This lesson is not available for purchase.", 404)
        amount = topic["price_kobo"]
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 100000 or topic["currency"] != "NGN":
            raise PaymentOrderError("invalid_price", "This lesson has invalid payment settings.", 503)
        existing = conn.execute(
            """SELECT 1 FROM entitlements WHERE student_id=%s AND topic_id=%s
               AND revoked_at IS NULL LIMIT 1""", (student_id, topic_id)
        ).fetchone()
        if existing:
            raise PaymentOrderError("already_owned", "You already have access to this lesson.", 409)
        conn.execute(
            """INSERT INTO payment_transactions
               (student_id,topic_id,provider,provider_reference,amount_kobo,currency,status)
               VALUES (%s,%s,'paystack',%s,%s,'NGN','initialized')""",
            (student_id, topic_id, reference, amount)
        )
        email = student["email"]
    try:
        checkout = _initialise_with_paystack(email, reference, amount, base_url + "/payment-return",
                                             secret, opener=opener)
    except Exception:
        with connection() as conn:
            conn.execute(
                """UPDATE payment_transactions SET status='failed'
                   WHERE provider_reference=%s AND status='initialized'""", (reference,)
            )
        raise
    return {"reference": reference, "amount_kobo": amount, "currency": "NGN",
            "topic_title": topic["title"], **checkout}
