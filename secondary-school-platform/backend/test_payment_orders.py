import json
import unittest
from unittest.mock import patch

from payment_orders import _initialise_with_paystack, PaymentOrderError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return json.dumps(self.payload).encode()


class PaymentOrderTests(unittest.TestCase):
    def test_initialisation_uses_server_amount_and_reference(self):
        seen = {}
        def opener(request, timeout):
            seen["url"] = request.full_url
            seen["body"] = json.loads(request.data.decode())
            seen["authorization"] = request.headers.get("Authorization")
            seen["timeout"] = timeout
            return FakeResponse({"status": True, "data": {
                "reference": "lw_order1", "authorization_url": "https://checkout.paystack.com/x",
                "access_code": "abc"
            }})
        result = _initialise_with_paystack(
            "student@example.com", "lw_order1", 125000, "https://learnwise.example/payment-return",
            "test-secret", opener=opener
        )
        self.assertEqual(seen["url"], "https://api.paystack.co/transaction/initialize")
        self.assertEqual(seen["body"]["amount"], 125000)
        self.assertEqual(seen["body"]["reference"], "lw_order1")
        self.assertEqual(seen["body"]["currency"], "NGN")
        self.assertEqual(seen["authorization"], "Bearer test-secret")
        self.assertEqual(result["authorization_url"], "https://checkout.paystack.com/x")

    def test_reference_mismatch_fails_closed(self):
        def opener(request, timeout):
            return FakeResponse({"status": True, "data": {
                "reference": "different", "authorization_url": "https://checkout.paystack.com/x"
            }})
        with self.assertRaises(PaymentOrderError):
            _initialise_with_paystack("student@example.com", "lw_expected", 100000,
                                      "https://learnwise.example/payment-return", "secret", opener=opener)

    def test_untrusted_checkout_host_fails_closed(self):
        def opener(request, timeout):
            return FakeResponse({"status": True, "data": {
                "reference": "lw_expected", "authorization_url": "https://attacker.example/checkout"
            }})
        with self.assertRaises(PaymentOrderError):
            _initialise_with_paystack("student@example.com", "lw_expected", 100000,
                                      "https://learnwise.example/payment-return", "secret", opener=opener)

    def test_provider_failure_fails_closed(self):
        def opener(request, timeout):
            return FakeResponse({"status": False, "message": "declined"})
        with self.assertRaises(PaymentOrderError):
            _initialise_with_paystack("student@example.com", "lw_expected", 100000,
                                      "https://learnwise.example/payment-return", "secret", opener=opener)


if __name__ == "__main__":
    unittest.main()
