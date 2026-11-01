import os
import unittest
from unittest.mock import patch

from payment_notifications import (
    DEFAULT_ALERT_RECIPIENT,
    build_payment_alert,
    send_owner_payment_alert,
)


class PaymentNotificationTests(unittest.TestCase):
    def setUp(self):
        self.payment = {
            "reference": "LW-ORDER-123",
            "currency": "NGN",
            "amount_major": "1500.00",
            "paid_at": "2026-11-01T12:30:00Z",
            "product": "Student onboarding",
        }

    def test_default_recipient_is_owner_gmail(self):
        self.assertEqual(DEFAULT_ALERT_RECIPIENT, "emmanuelbjephter@gmail.com")

    def test_message_contains_reconciliation_fields(self):
        subject, body = build_payment_alert(self.payment)
        self.assertIn("LW-ORDER-123", subject)
        self.assertIn("NGN 1,500.00", body)
        self.assertIn("Paid at: 2026-11-01T12:30:00Z", body)

    def test_rejects_incomplete_or_invalid_payment(self):
        for changed in (
            {"reference": ""},
            {"currency": "NIG"},
            {"amount_major": "-1"},
            {"paid_at": ""},
        ):
            payment = {**self.payment, **changed}
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                build_payment_alert(payment)

    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.example.test",
        "SMTP_USERNAME": "mailer@example.test",
        "SMTP_PASSWORD": "test-secret",
        "SMTP_FROM": "mailer@example.test",
        "PAYMENT_ALERT_RECIPIENT": "emmanuelbjephter@gmail.com",
        "SMTP_PORT": "587",
    }, clear=True)
    @patch("payment_notifications.smtplib.SMTP")
    def test_sends_only_to_configured_owner(self, smtp_class):
        smtp = smtp_class.return_value.__enter__.return_value
        self.assertTrue(send_owner_payment_alert(self.payment))
        message = smtp.send_message.call_args.args[0]
        self.assertEqual(message["To"], "emmanuelbjephter@gmail.com")
        self.assertIn("LW-ORDER-123", message["Subject"])
        smtp.starttls.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_fails_closed_without_mail_provider(self):
        with self.assertRaises(RuntimeError):
            send_owner_payment_alert(self.payment)


if __name__ == "__main__":
    unittest.main()
