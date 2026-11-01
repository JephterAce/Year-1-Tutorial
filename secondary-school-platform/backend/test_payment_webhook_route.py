import unittest
from unittest.mock import patch

from app import app


class PaystackWebhookRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("payments.process_paystack_charge_success")
    def test_accepts_verified_callback_and_returns_success(self, process):
        process.return_value = {"status": "successful", "reference": "LW-1", "notification": "queued"}
        response = self.client.post(
            "/api/v1/webhooks/paystack",
            data=b'{"event":"charge.success"}',
            headers={"x-paystack-signature": "signed"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["received"])

    @patch("payments.process_paystack_charge_success")
    def test_invalid_signature_returns_400(self, process):
        from paystack_webhooks import PaystackWebhookError
        process.side_effect = PaystackWebhookError("invalid")
        response = self.client.post(
            "/api/v1/webhooks/paystack", data=b"{}", headers={"x-paystack-signature": "bad"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("payments.process_paystack_charge_success")
    def test_temporary_fulfilment_failure_returns_retryable_503(self, process):
        from payments import PaymentProcessingError
        process.side_effect = PaymentProcessingError("temporarily unavailable")
        response = self.client.post(
            "/api/v1/webhooks/paystack", data=b"{}", headers={"x-paystack-signature": "signed"}
        )
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
