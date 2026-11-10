import hashlib
import hmac
import json
import os
import unittest
from unittest.mock import patch

from payments import process_paystack_charge_success, PaymentProcessingError


class PaymentOrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.secret = "test-secret"
        self.body = json.dumps({
            "event": "charge.success",
            "data": {"reference": "LW-1", "amount": 100000, "currency": "NGN", "status": "success"},
        }).encode()
        self.signature = hmac.new(self.secret.encode(), self.body, hashlib.sha512).hexdigest()
        self.env = patch.dict(os.environ, {"PAYSTACK_SECRET_KEY": self.secret})
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("database.fulfil_verified_payment")
    @patch("payments.verify_paystack_transaction")
    @patch("database.get_pending_paystack_order")
    def test_requires_order_then_remote_verification_then_atomic_fulfilment(self, order, verify, fulfil):
        order.return_value = {"reference": "LW-1", "amount_kobo": 100000}
        verify.return_value = {
            "reference": "LW-1", "amount_kobo": 100000,
            "currency": "NGN", "status": "success", "paid_at": "2026-11-01T10:00:00Z",
        }
        fulfil.return_value = {"status": "successful", "reference": "LW-1", "notification": "queued"}
        result = process_paystack_charge_success(self.body, self.signature)
        self.assertEqual(result["status"], "successful")
        order.assert_called_once_with("LW-1")
        verify.assert_called_once()
        fulfil.assert_called_once()

    @patch("database.get_pending_paystack_order")
    def test_rejects_webhook_without_matching_order(self, order):
        order.side_effect = ValueError("missing")
        with self.assertRaises(PaymentProcessingError):
            process_paystack_charge_success(self.body, self.signature)

    @patch("database.get_pending_paystack_order")
    def test_rejects_invalid_webhook_signature(self, order):
        with self.assertRaises(ValueError):
            process_paystack_charge_success(self.body, "invalid")
        order.assert_not_called()

    @patch("database.fulfil_verified_payment")
    @patch("payments.verify_paystack_transaction")
    @patch("database.get_pending_paystack_order")
    def test_rejects_order_amount_mismatch_before_remote_verification(self, order, verify, fulfil):
        order.return_value = {"reference": "LW-1", "amount_kobo": 99999}
        with self.assertRaises(PaymentProcessingError):
            process_paystack_charge_success(self.body, self.signature)
        verify.assert_not_called()
        fulfil.assert_not_called()


if __name__ == "__main__":
    unittest.main()
