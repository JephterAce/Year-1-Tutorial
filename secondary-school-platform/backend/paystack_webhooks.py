"""Paystack webhook signature and event-shape validation primitives.

These helpers authenticate the raw webhook body and validate its basic shape.
They do NOT fetch the transaction from Paystack, compare it with a server-side
order, write payment state, grant entitlements, or send email. Do not fulfil a
purchase using this module alone.
"""
import hashlib
import hmac
import json


class PaystackWebhookError(ValueError):
    """Raised when a webhook cannot be authenticated or safely interpreted."""


def verify_paystack_signature(raw_body, signature, secret):
    """Verify Paystack's HMAC-SHA512 signature over the exact raw request bytes."""
    if not isinstance(raw_body, (bytes, bytearray)) or not raw_body:
        return False
    if not isinstance(signature, str) or not signature or not isinstance(secret, str) or not secret:
        return False
    expected = hmac.new(
        secret.encode("utf-8"), bytes(raw_body), hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature.strip().lower())


def parse_verified_paystack_event(raw_body, signature, secret):
    """Authenticate and validate a charge.success event's minimum safe fields."""
    if not verify_paystack_signature(raw_body, signature, secret):
        raise PaystackWebhookError("Invalid Paystack webhook signature")
    try:
        event = json.loads(bytes(raw_body).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise PaystackWebhookError("Webhook body is not valid JSON")
    if not isinstance(event, dict) or event.get("event") != "charge.success":
        raise PaystackWebhookError("Unsupported Paystack event")
    data = event.get("data")
    if not isinstance(data, dict):
        raise PaystackWebhookError("Webhook data is missing")
    reference = data.get("reference")
    amount = data.get("amount")
    currency = data.get("currency")
    status = data.get("status")
    if not isinstance(reference, str) or not reference.strip() or len(reference) > 120:
        raise PaystackWebhookError("Invalid payment reference")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise PaystackWebhookError("Invalid payment amount")
    if currency != "NGN" or status != "success":
        raise PaystackWebhookError("Payment currency or status is not accepted")
    # Return only the minimal fields required for a subsequent server-side lookup.
    return {
        "event": "charge.success",
        "reference": reference.strip(),
        "amount_kobo": amount,
        "currency": "NGN",
    }
