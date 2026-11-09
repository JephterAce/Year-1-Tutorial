"""Brevo HTTPS transactional delivery for identity and admin messages; never logs bearer tokens."""
import json
import os
from email.utils import parseaddr
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode


BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoConfigurationError(RuntimeError):
    """Safe configuration failure; contains only the missing/invalid setting name."""
    def __init__(self, setting, category="configuration_error"):
        self.setting = setting
        self.category = category
        super().__init__(category)


class BrevoDeliveryError(RuntimeError):
    """Provider failure with deliberately bounded, non-sensitive diagnostic metadata."""
    def __init__(self, category, http_status=None, provider_error_code=None):
        self.category = category
        self.http_status = http_status if isinstance(http_status, int) and 100 <= http_status <= 599 else None
        # Provider codes are identifiers, not messages. Accept only short ASCII tokens.
        safe = provider_error_code if isinstance(provider_error_code, str) else ""
        import re
        self.provider_error_code = safe[:64] if re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", safe) else None
        super().__init__(category)


def _safe_provider_code(error):
    """Extract only Brevo's machine-readable 'code'; never expose its message/body."""
    try:
        payload = json.loads(error.read(8192).decode("utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    code = payload.get("code")
    if isinstance(code, str):
        import re
        if re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", code):
            return code
    return None


def _required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise BrevoConfigurationError(name, "missing_configuration")
    return value


def _sender():
    email = _required("BREVO_SENDER_EMAIL")
    if parseaddr(email)[1] != email:
        raise BrevoConfigurationError("BREVO_SENDER_EMAIL", "invalid_configuration")
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
        raise BrevoDeliveryError("provider_rejected_request", int(exc.code), _safe_provider_code(exc)) from None
    except (URLError, TimeoutError, OSError):
        raise BrevoDeliveryError("connection_error") from None
    if status not in (200, 201, 202):
        raise BrevoDeliveryError("unexpected_http_status", status)
    try:
        result = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BrevoDeliveryError("invalid_provider_response", status) from None
    if not isinstance(result, dict) or not isinstance(result.get("messageId"), str):
        raise BrevoDeliveryError("missing_message_acknowledgement", status)
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
    _send(email, subject, f"{intro} using this one-time link:\n\n{url}\n\nIf you did not request this, ignore this email. Do not share this link.")


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
        "It is not a real learner account and must not be used with real learner information.\n\n"
        f"Verify the mailbox using this one-time link (expires in 30 minutes):\n{url}\n\n"
        f"Temporary staging password (account expires within 24 hours):\n{temporary_password}\n\n"
        "Do not reuse this password or share the verification link. "
        "This synthetic account has no guardian-consent status and is blocked from learner records, "
        "assessments, payments, exports and private learning content."
    )
