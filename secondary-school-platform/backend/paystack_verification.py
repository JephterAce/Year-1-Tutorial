"""Server-to-server Paystack transaction verification.

Uses the Paystack verify endpoint with a server-held secret. A successful result
is still only evidence to be compared with a pending Learnwise order before
fulfilment; never grant access based on a checkout redirect or webhook alone.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class PaystackVerificationError(ValueError):
    pass


def verify_paystack_transaction(reference, expected_amount_kobo, secret=None, opener=urlopen):
    if not isinstance(reference, str) or not reference.strip() or len(reference) > 120:
        raise PaystackVerificationError("Invalid payment reference")
    if isinstance(expected_amount_kobo, bool) or not isinstance(expected_amount_kobo, int) or expected_amount_kobo <= 0:
        raise PaystackVerificationError("Invalid expected payment amount")
    secret = secret if secret is not None else os.environ.get("PAYSTACK_SECRET_KEY", "")
    if not isinstance(secret, str) or not secret.strip():
        raise PaystackVerificationError("Paystack secret is not configured")

    url = "https://api.paystack.co/transaction/verify/" + quote(reference.strip(), safe="")
    request = Request(url, headers={
        "Authorization": "Bearer " + secret.strip(),
        "Accept": "application/json",
    })
    try:
        with opener(request, timeout=10) as response:
            raw = response.read()
        payload = json.loads(raw.decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PaystackVerificationError("Paystack verification is temporarily unavailable") from exc

    if not isinstance(payload, dict) or payload.get("status") is not True:
        raise PaystackVerificationError("Paystack did not confirm the transaction")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise PaystackVerificationError("Paystack verification response is incomplete")
    if data.get("status") != "success":
        raise PaystackVerificationError("Transaction is not successful")
    if data.get("reference") != reference.strip():
        raise PaystackVerificationError("Transaction reference mismatch")
    amount = data.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount != expected_amount_kobo:
        raise PaystackVerificationError("Transaction amount mismatch")
    if data.get("currency") != "NGN":
        raise PaystackVerificationError("Transaction currency is not supported")
    return {
        "reference": reference.strip(),
        "amount_kobo": amount,
        "currency": "NGN",
        "status": "success",
        "paid_at": data.get("paid_at"),
    }
