"""Paystack webhook orchestration for authenticated, server-verified payments."""
import os

from paystack_webhooks import parse_verified_paystack_event, PaystackWebhookError
from paystack_verification import verify_paystack_transaction, PaystackVerificationError


class PaymentProcessingError(RuntimeError):
    pass


def process_paystack_charge_success(raw_body, signature):
    """Authenticate webhook, verify against Paystack, then atomically fulfil order.

    No checkout redirect is trusted. DB fulfilment requires an existing
    server-created order and records payment, entitlement and email outbox in
    one transaction. SMTP is deliberately not called here.
    """
    secret = os.environ.get("PAYSTACK_SECRET_KEY", "")
    try:
        event = parse_verified_paystack_event(raw_body, signature, secret)
    except PaystackWebhookError:
        raise

    from database import get_pending_paystack_order, fulfil_verified_payment
    try:
        order = get_pending_paystack_order(event["reference"])
    except Exception as exc:
        raise PaymentProcessingError("No eligible Learnwise order matches this payment") from exc

    if order["amount_kobo"] != event["amount_kobo"]:
        raise PaymentProcessingError("Webhook amount does not match the Learnwise order")

    try:
        verified = verify_paystack_transaction(
            order["reference"], order["amount_kobo"], secret=secret
        )
    except PaystackVerificationError as exc:
        raise PaymentProcessingError("Paystack transaction verification failed") from exc

    try:
        return fulfil_verified_payment(order["reference"], verified)
    except Exception as exc:
        raise PaymentProcessingError("Verified payment could not be safely recorded") from exc
