"""Brevo HTTPS transactional delivery for identity and admin messages; never logs bearer tokens."""
import json
import os
import re
from email.utils import parseaddr
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode


BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


def _required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def _sender():
    email = _required("BREVO_SENDER_EMAIL")
    if parseaddr(email)[1] != email:
        raise RuntimeError("Brevo sender email is invalid")
    name = os.environ.get("BREVO_SENDER_NAME", "Think Tank").strip()[:70]
    return {"email": email, "name": name}


def _send(recipient, subject, body):
    recipient = recipient.strip()
    if not recipient or parseaddr(recipient)[1] != recipient:
        raise RuntimeError("Email recipient is invalid")
    api_key = _required("BREVO_API_KEY")
    payload = {
        "sender": _sender(),
        "to": [{"email": recipient}],
        "subject": subject[:180],
        "textContent": body,
    }
    request = Request(
        BREVO_SEND_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            status = int(response.status)
            response_body = response.read(8192)
    except HTTPError as exc:
        # Do not surface provider response bodies; they can contain recipient or account data.
        raise RuntimeError(f"Brevo API rejected the message (HTTP {int(exc.code)}).") from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("Brevo API connection failed.") from None
    if status not in (200, 201, 202):
        raise RuntimeError(f"Brevo API returned unexpected HTTP {status}.")
    try:
        result = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("Brevo API returned an invalid response.") from None
    if not isinstance(result, dict) or not isinstance(result.get("messageId"), str):
        raise RuntimeError("Brevo did not acknowledge the transactional message.")
    return result["messageId"]


def send_identity_link(email, token, purpose):
    base = _required("PUBLIC_APP_URL").rstrip("/")
    if not base.startswith("https://"):
        raise RuntimeError("PUBLIC_APP_URL must use HTTPS")
    if purpose == "verify":
        action, subject, intro = "verify", "Verify your Think Tank email", "Verify your email address"
    elif purpose == "reset":
        action, subject, intro = "reset", "Reset your Think Tank password", "Reset your password"
    else:
        raise ValueError("Unsupported identity email purpose")
    url = f"{base}/account.html?{urlencode({'action': action, 'token': token})}"
    _send(email, subject, f"{intro} using this one-time link:\\n\\n{url}\\n\\nIf you did not request this, ignore this email. Do not share this link.")


def send_admin_diagnostic(email):
    """Send a fixed, token-free HTTPS API diagnostic to the admin."""
    return _send(
        email,
        "Think Tank staging email-delivery test",
        "This is a diagnostic message initiated by an authenticated Think Tank administrator. "
        "It confirms that the staging application can submit email through the configured Brevo API. "
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
    return _send(
        email,
        "Think Tank staging synthetic QA invitation",
        "A short-lived synthetic QA identity was created for controlled staging acceptance. "
        "It is not a real learner account and must not be used with real learner information.\\n\\n"
        f"Verify the mailbox using this one-time link (expires in 30 minutes):\\n{url}\\n\\n"
        f"Temporary staging password (account expires within 24 hours):\\n{temporary_password}\\n\\n"
        "Do not reuse this password or share the verification link. "
        "This synthetic account has no guardian-consent status and is blocked from learner records, "
        "assessments, payments, exports and private learning content."
    )
