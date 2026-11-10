import hashlib
import hmac
import json
import unittest

from paystack_webhooks import (
    PaystackWebhookError,
    parse_verified_paystack_event,
    verify_paystack_signature,
)


class PaystackWebhookSecurityTests(unittest.TestCase):
    secret = "test-secret-not-for-production"

    def payload(self, **overrides):
        data = {
            "reference": "LW-ORDER-123",
            "amount": 150000,
            "currency": "NGN",
            "status": "success",
        }
        data.update(overrides)
        return json.dumps({"event": "charge.success", "data": data}).encode()

    def signature(self, body):
        return hmac.new(self.secret.encode(), body, hashlib.sha512).hexdigest()

    def test_accepts_valid_raw_body_signature(self):
        body = self.payload()
        self.assertTrue(verify_paystack_signature(body, self.signature(body), self.secret))

    def test_rejects_modified_body_and_bad_signature(self):
        body = self.payload()
        self.assertFalse(verify_paystack_signature(body + b" ", self.signature(body), self.secret))
        self.assertFalse(verify_paystack_signature(body, "bad", self.secret))

    def test_extracts_only_minimal_verified_event_fields(self):
        body = self.payload()
        result = parse_verified_paystack_event(body, self.signature(body), self.secret)
        self.assertEqual(result, {
            "event": "charge.success",
            "reference": "LW-ORDER-123",
            "amount_kobo": 150000,
            "currency": "NGN",
        })

    def test_rejects_invalid_signature_before_parsing(self):
        with self.assertRaises(PaystackWebhookError):
            parse_verified_paystack_event(b"not json", "bad", self.secret)

    def test_rejects_unsupported_event(self):
        body = json.dumps({"event": "transfer.success", "data": {}}).encode()
        with self.assertRaises(PaystackWebhookError):
            parse_verified_paystack_event(body, self.signature(body), self.secret)

    def test_rejects_non_ngn_or_unsuccessful_payment(self):
        for changes in ({"currency": "USD"}, {"status": "pending"}):
            body = self.payload(**changes)
            with self.subTest(changes=changes), self.assertRaises(PaystackWebhookError):
                parse_verified_paystack_event(body, self.signature(body), self.secret)

    def test_rejects_invalid_amounts_and_reference(self):
        for changes in (
            {"amount": True}, {"amount": 0}, {"amount": -10},
            {"amount": "150000"}, {"reference": ""},
        ):
            body = self.payload(**changes)
            with self.subTest(changes=changes), self.assertRaises(PaystackWebhookError):
                parse_verified_paystack_event(body, self.signature(body), self.secret)


if __name__ == "__main__":
    unittest.main()
