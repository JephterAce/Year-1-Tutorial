import json
import io
import os
import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError

import identity_email


class BrevoDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "BREVO_API_KEY": "test-api-key",
            "BREVO_SENDER_EMAIL": "verified@example.test",
            "BREVO_SENDER_NAME": "Think Tank",
            "PUBLIC_APP_URL": "https://learnwise-staging-api.onrender.com",
            "APP_ENV": "staging",
        }
        self.patch_env = patch.dict(os.environ, self.env, clear=True)
        self.patch_env.start()

    def tearDown(self):
        self.patch_env.stop()

    def test_transactional_message_uses_brevo_https_api(self):
        response = Mock()
        response.status = 201
        response.read.return_value = b'{"messageId":"accepted-id"}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with patch("identity_email.urlopen", return_value=response) as send:
            message_id = identity_email._send("student@example.test", "Verify", "One-time link")
        self.assertEqual(message_id, "accepted-id")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, identity_email.BREVO_SEND_URL)
        self.assertEqual(request.get_header("Api-key"), "test-api-key")
        self.assertEqual(json.loads(request.data)["to"][0]["email"], "student@example.test")

    def test_identity_link_keeps_verification_action_and_one_time_token(self):
        response = Mock()
        response.status = 201
        response.read.return_value = b'{"messageId":"accepted-id"}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with patch("identity_email.urlopen", return_value=response) as send:
            identity_email.send_identity_link("student@example.test", "one-time-token", "verify")
        body = json.loads(send.call_args.args[0].data)["textContent"]
        self.assertIn("action=verify", body)
        self.assertIn("token=one-time-token", body)

    def test_401_exposes_only_safe_status_and_provider_code(self):
        private_body = json.dumps({
            "code": "unauthorized",
            "message": "private account detail and recipient@example.test",
        }).encode()
        error = HTTPError(
            identity_email.BREVO_SEND_URL, 401, "unauthorized", {},
            io.BytesIO(private_body),
        )
        with patch("identity_email.urlopen", side_effect=error):
            with self.assertRaises(identity_email.BrevoDeliveryError) as caught:
                identity_email._send("student@example.test", "Verify", "Body")
        self.assertEqual(caught.exception.http_status, 401)
        self.assertEqual(caught.exception.provider_error_code, "unauthorized")
        self.assertNotIn("private", str(caught.exception))
        self.assertNotIn("recipient@example.test", str(caught.exception))

    def test_400_exposes_bounded_provider_code_but_not_message(self):
        private_body = json.dumps({
            "code": "invalid_parameter",
            "message": "sender owner@example.test is not accepted",
        }).encode()
        error = HTTPError(
            identity_email.BREVO_SEND_URL, 400, "bad request", {},
            io.BytesIO(private_body),
        )
        with patch("identity_email.urlopen", side_effect=error):
            with self.assertRaises(identity_email.BrevoDeliveryError) as caught:
                identity_email._send("student@example.test", "Verify", "Body")
        self.assertEqual(caught.exception.http_status, 400)
        self.assertEqual(caught.exception.provider_error_code, "invalid_parameter")
        self.assertNotIn("owner@example.test", str(caught.exception))

    def test_malicious_provider_code_is_discarded(self):
        error = HTTPError(
            identity_email.BREVO_SEND_URL, 403, "forbidden", {},
            io.BytesIO(b'{"code":"bad code with private data","message":"secret"}'),
        )
        with patch("identity_email.urlopen", side_effect=error):
            with self.assertRaises(identity_email.BrevoDeliveryError) as caught:
                identity_email._send("student@example.test", "Verify", "Body")
        self.assertIsNone(caught.exception.provider_error_code)

    def test_missing_api_key_reports_only_setting_name(self):
        os.environ.pop("BREVO_API_KEY")
        with self.assertRaises(identity_email.BrevoConfigurationError) as caught:
            identity_email._send("student@example.test", "Verify", "Body")
        self.assertEqual(caught.exception.setting, "BREVO_API_KEY")
        self.assertEqual(caught.exception.category, "missing_configuration")

    def test_connection_failure_has_no_provider_status(self):
        from urllib.error import URLError
        with patch("identity_email.urlopen", side_effect=URLError("private endpoint detail")):
            with self.assertRaises(identity_email.BrevoDeliveryError) as caught:
                identity_email._send("student@example.test", "Verify", "Body")
        self.assertEqual(caught.exception.category, "connection_error")
        self.assertIsNone(caught.exception.http_status)
        self.assertIsNone(caught.exception.provider_error_code)


if __name__ == "__main__":
    unittest.main()
