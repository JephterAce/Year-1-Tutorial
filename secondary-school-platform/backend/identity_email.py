"""SMTP delivery for student identity messages; never logs bearer tokens."""
import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr
from urllib.parse import urlencode


def _required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def _send(recipient, subject, body):
    recipient = recipient.strip()
    sender = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USERNAME", "")).strip()
    if not recipient or parseaddr(recipient)[1] != recipient or not sender or parseaddr(sender)[1] != sender:
        raise RuntimeError("Email sender or recipient is invalid")
    host, username, password = _required("SMTP_HOST"), _required("SMTP_USERNAME"), _required("SMTP_PASSWORD")
    port = int(os.environ.get("SMTP_PORT", "587"))
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, subject
    message.set_content(body)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)


def send_identity_link(email, token, purpose):
    base = _required("PUBLIC_APP_URL").rstrip("/")
    if not base.startswith("https://"):
        raise RuntimeError("PUBLIC_APP_URL must use HTTPS")
    if purpose == "verify":
        action, subject, intro = "verify", "Verify your Learnwise email", "Verify your email address"
    elif purpose == "reset":
        action, subject, intro = "reset", "Reset your Learnwise password", "Reset your password"
    else:
        raise ValueError("Unsupported identity email purpose")
    url = f"{base}/account.html?{urlencode({'action': action, 'token': token})}"
    _send(email, subject, f"{intro} using this one-time link:\n\n{url}\n\nIf you did not request this, ignore this email. Do not share this link.")


def send_admin_diagnostic(email):
    """Send a fixed, token-free SMTP connectivity diagnostic to the admin."""
    _send(
        email,
        "Think Tank staging email-delivery test",
        "This is a diagnostic message initiated by an authenticated Think Tank administrator. "
        "It confirms that the staging application can submit email through its configured SMTP provider. "
        "No action is required. If you did not initiate this test, notify the system owner.",
    )



def send_synthetic_qa_invite(email, token, temporary_password):
    """Send a short-lived staging-only QA invitation; never log its credentials."""
    if os.environ.get("APP_ENV", "").strip().lower() != "staging":
        raise RuntimeError("Synthetic QA invitations are staging-only")
    base = _required("PUBLIC_APP_URL").rstrip("/")
    if not base.startswith("https://"):
        raise RuntimeError("PUBLIC_APP_URL must use HTTPS")
    url = f"{base}/account.html?{urlencode({'action': 'verify', 'token': token})}"
    _send(
        email,
        "Think Tank staging synthetic QA invitation",
        "A short-lived synthetic QA identity was created for controlled staging acceptance. "
        "It is not a real learner account and must not be used with real learner information.\n\n"
        f"Verify the mailbox using this one-time link (expires in 30 minutes):\n{url}\n\n"
        f"Temporary staging password (account expires within 24 hours):\n{temporary_password}\n\n"
        "Do not reuse this password or share the verification link. "
        "This synthetic account has no guardian-consent status and is blocked from learner records, "
        "assessments, payments, exports and private learning content."
    )
