import json
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

    def test_provider_response_body_is_not_exposed(self):
        error = HTTPError(identity_email.BREVO_SEND_URL, 401, "unauthorized", {}, None)
        with patch("identity_email.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "HTTP 401"):
                identity_email._send("student@example.test", "Verify", "Body")

    def test_sender_and_api_key_are_required(self):
        os.environ.pop("BREVO_API_KEY")
        with self.assertRaisesRegex(RuntimeError, "BREVO_API_KEY"):
            identity_email._send("student@example.test", "Verify", "Body")


if __name__ == "__main__":
    unittest.main()
