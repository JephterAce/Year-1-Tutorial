import os
import unittest
from unittest.mock import patch

from identity_email import send_identity_link, send_admin_diagnostic


class IdentityEmailDeliveryTests(unittest.TestCase):
    def test_verification_message_uses_starttls_and_one_time_link(self):
        env = {
            "PUBLIC_APP_URL": "https://thinktank.example.test",
            "SMTP_HOST": "smtp.example.test",
            "SMTP_USERNAME": "ci-smtp-user",
            "SMTP_PASSWORD": "ci-smtp-password",
            "SMTP_FROM": "no-reply@example.test",
            "SMTP_PORT": "587",
        }
        with patch.dict(os.environ, env), patch("identity_email.smtplib.SMTP") as smtp_class:
            client = smtp_class.return_value.__enter__.return_value
            send_identity_link("student@example.test", "one-time-token", "verify")
        smtp_class.assert_called_once_with("smtp.example.test", 587, timeout=10)
        client.starttls.assert_called_once()
        client.login.assert_called_once_with("ci-smtp-user", "ci-smtp-password")
        message = client.send_message.call_args.args[0]
        self.assertEqual(message["To"], "student@example.test")
        self.assertIn("one-time-token", message.get_content())

    def test_password_reset_uses_ssl_on_port_465(self):
        env = {
            "PUBLIC_APP_URL": "https://thinktank.example.test",
            "SMTP_HOST": "smtp.example.test",
            "SMTP_USERNAME": "ci-smtp-user",
            "SMTP_PASSWORD": "ci-smtp-password",
            "SMTP_FROM": "no-reply@example.test",
            "SMTP_PORT": "465",
        }
        with patch.dict(os.environ, env), patch("identity_email.smtplib.SMTP_SSL") as smtp_class:
            client = smtp_class.return_value.__enter__.return_value
            send_identity_link("student@example.test", "reset-token", "reset")
        smtp_class.assert_called_once_with("smtp.example.test", 465, timeout=10)
        client.login.assert_called_once_with("ci-smtp-user", "ci-smtp-password")
        client.send_message.assert_called_once()

    def test_non_https_public_app_url_is_rejected(self):
        with patch.dict(os.environ, {"PUBLIC_APP_URL": "http://thinktank.example.test"}):
            with self.assertRaises(RuntimeError):
                send_identity_link("student@example.test", "token", "verify")

    def test_unsupported_email_purpose_is_rejected(self):
        with patch.dict(os.environ, {"PUBLIC_APP_URL": "https://thinktank.example.test"}):
            with self.assertRaises(ValueError):
                send_identity_link("student@example.test", "token", "other")

    def test_admin_diagnostic_contains_no_token_or_link(self):
        env = {
            "SMTP_HOST": "smtp.example.test",
            "SMTP_USERNAME": "ci-smtp-user",
            "SMTP_PASSWORD": "ci-smtp-password",
            "SMTP_FROM": "no-reply@example.test",
            "SMTP_PORT": "587",
        }
        with patch.dict(os.environ, env), patch("identity_email.smtplib.SMTP") as smtp_class:
            client = smtp_class.return_value.__enter__.return_value
            send_admin_diagnostic("admin@example.test")
        message = client.send_message.call_args.args[0]
        self.assertEqual(message["To"], "admin@example.test")
        self.assertIn("staging email-delivery test", message["Subject"])
        self.assertNotIn("token=", message.get_content())
        self.assertNotIn("https://", message.get_content())


if __name__ == "__main__":
    unittest.main()
