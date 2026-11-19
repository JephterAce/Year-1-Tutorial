"""Owner payment-alert email delivery for verified payment events.

This module sends a minimal notification through an explicitly configured SMTP
relay. It does not verify Paystack webhooks or decide whether a payment succeeded;
only a trusted webhook/payment service may call it after server-side verification.
"""
import os
import smtplib
from email.message import EmailMessage
from decimal import Decimal, InvalidOperation
from email.utils import parseaddr


DEFAULT_ALERT_RECIPIENT = "emmanuelbjephter@gmail.com"


def _required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def _valid_email(value):
    if not isinstance(value, str):
        return False
    address = parseaddr(value.strip())[1]
    return bool(address and address == value.strip() and "@" in address)


def build_payment_alert(payment):
    """Build a plain-text alert from a verified, allow-listed payment summary."""
    if not isinstance(payment, dict):
        raise ValueError("Payment summary must be an object")

    reference = str(payment.get("reference", "")).strip()
    currency = str(payment.get("currency", "")).strip().upper()
    paid_at = str(payment.get("paid_at", "")).strip()
    product = str(payment.get("product", "Student onboarding")).strip()
    amount_raw = payment.get("amount_major")

    if not reference or len(reference) > 120:
        raise ValueError("A valid payment reference is required")
    if currency != "NGN":
        raise ValueError("Learnwise currently accepts NGN payments only")
    if not paid_at or len(paid_at) > 80:
        raise ValueError("A payment timestamp is required")
    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("A valid payment amount is required")
    if not amount.is_finite() or amount < 0:
        raise ValueError("A valid payment amount is required")

    safe_product = " ".join(product.split())[:100] or "Student onboarding"
    subject = f"Learnwise payment successful — {reference}"
    body = (
        "A successful Learnwise payment has been confirmed by the payment service.\n\n"
        f"Product: {safe_product}\n"
        f"Amount: {currency} {amount:,.2f}\n"
        f"Payment reference: {reference}\n"
        f"Paid at: {paid_at}\n\n"
        "This is an administrative notification. Check the Paystack dashboard "
        "for the authoritative transaction record.\n"
    )
    return subject, body


def send_owner_payment_alert(payment):
    """Send an owner alert. Call only after Paystack signature and transaction checks."""
    recipient = os.environ.get("PAYMENT_ALERT_RECIPIENT", DEFAULT_ALERT_RECIPIENT).strip()
    if not _valid_email(recipient):
        raise RuntimeError("PAYMENT_ALERT_RECIPIENT is invalid")

    host = _required_env("SMTP_HOST")
    username = _required_env("SMTP_USERNAME")
    password = _required_env("SMTP_PASSWORD")
    sender = os.environ.get("SMTP_FROM", username).strip()
    if not _valid_email(sender):
        raise RuntimeError("SMTP_FROM is invalid")
    try:
        port = int(os.environ.get("SMTP_PORT", "587"))
    except ValueError:
        raise RuntimeError("SMTP_PORT must be an integer")
    if not 1 <= port <= 65535:
        raise RuntimeError("SMTP_PORT is out of range")

    subject, body = build_payment_alert(payment)
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    timeout = 10
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=timeout) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
    return True
