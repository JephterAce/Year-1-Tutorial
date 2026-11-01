import json
import unittest
from urllib.request import Request

from paystack_verification import PaystackVerificationError, verify_paystack_transaction


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        return False
    def read(self):
        return self.payload


class PaystackVerificationTests(unittest.TestCase):
    def response(self, **changes):
        data = {
            "status": "success", "reference": "LW-123",
            "amount": 125000, "currency": "NGN", "paid_at": "2026-11-01T10:00:00Z",
        }
        data.update(changes)
        return {"status": True, "data": data}

    def test_verifies_server_side_transaction_and_sends_bearer_auth(self):
        seen = {}
        def opener(request, timeout):
            seen["request"] = request
            seen["timeout"] = timeout
            return FakeResponse(self.response())
        result = verify_paystack_transaction("LW-123", 125000, "sk_test_secret", opener)
        self.assertEqual(result["status"], "success")
        self.assertEqual(seen["request"].get_header("Authorization"), "Bearer sk_test_secret")
        self.assertEqual(seen["timeout"], 10)

    def test_rejects_reference_amount_currency_and_status_mismatches(self):
        for changes in (
            {"reference": "OTHER"}, {"amount": 1},
            {"currency": "USD"}, {"status": "pending"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(PaystackVerificationError):
                    verify_paystack_transaction(
                        "LW-123", 125000, "sk_test_secret",
                        lambda *_args, **_kwargs: FakeResponse(self.response(**changes)),
                    )

    def test_rejects_missing_secret_and_bad_expected_amount(self):
        with self.assertRaises(PaystackVerificationError):
            verify_paystack_transaction("LW-123", 125000, "", lambda *_a, **_k: None)
        with self.assertRaises(PaystackVerificationError):
            verify_paystack_transaction("LW-123", True, "secret", lambda *_a, **_k: None)

    def test_rejects_provider_failure(self):
        with self.assertRaises(PaystackVerificationError):
            verify_paystack_transaction("LW-123", 125000, "secret",
                lambda *_a, **_k: FakeResponse({"status": False}))


if __name__ == "__main__":
    unittest.main()
