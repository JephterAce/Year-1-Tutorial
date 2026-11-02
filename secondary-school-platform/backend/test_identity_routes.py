import os
import unittest
from unittest.mock import patch

from app import app


class StudentIdentityRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_registration_requires_explicit_terms_and_privacy_acceptance(self):
        response = self.client.post("/api/v1/auth/register", json={
            "email": "learner@example.com", "username": "learner_1",
            "display_name": "Learner One", "class_level": "SS1",
            "password": "a sufficiently long password",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "consent_required")

    @patch("identity_email.send_identity_link")
    @patch("identity_service.register_student")
    def test_registration_sends_verification_without_returning_token(self, register, send):
        register.return_value = {
            "student": {"email": "learner@example.com"},
            "verification_token": "secret-one-time-token",
        }
        response = self.client.post("/api/v1/auth/register", json={
            "email": "learner@example.com", "username": "learner_1",
            "display_name": "Learner One", "class_level": "SS1",
            "password": "a sufficiently long password",
            "accept_terms": True, "accept_privacy": True,
        })
        self.assertEqual(response.status_code, 202)
        self.assertNotIn("secret-one-time-token", response.get_data(as_text=True))
        send.assert_called_once_with("learner@example.com", "secret-one-time-token", "verify")

    @patch("identity_service.login_student")
    def test_login_sets_http_only_session_and_readable_csrf_cookie(self, login):
        login.return_value = {
            "session_id": "s" * 44, "csrf_token": "c" * 44, "student_id": "student-id"
        }
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            response = self.client.post("/api/v1/auth/login", json={
                "email": "learner@example.com", "password": "long-password"
            })
        self.assertEqual(response.status_code, 200)
        cookies = response.headers.getlist("Set-Cookie")
        session_cookie = next(x for x in cookies if x.startswith("learnwise_session="))
        csrf_cookie = next(x for x in cookies if x.startswith("learnwise_csrf="))
        self.assertIn("HttpOnly", session_cookie)
        self.assertIn("Secure", session_cookie)
        self.assertIn("SameSite=Lax", session_cookie)
        self.assertNotIn("HttpOnly", csrf_cookie)
        self.assertIn("Secure", csrf_cookie)

    @patch("identity_service.login_student")
    def test_login_marks_cookies_secure_in_staging(self, login):
        login.return_value = {
            "session_id": "s" * 44, "csrf_token": "c" * 44, "student_id": "student-id"
        }
        with patch.dict(os.environ, {"APP_ENV": "staging"}):
            response = self.client.post("/api/v1/auth/login", json={
                "email": "learner@example.com", "password": "long-password"
            })
        self.assertEqual(response.status_code, 200)
        cookies = response.headers.getlist("Set-Cookie")
        self.assertTrue(any(x.startswith("learnwise_session=") and "Secure" in x for x in cookies))
        self.assertTrue(any(x.startswith("learnwise_csrf=") and "Secure" in x for x in cookies))

    def test_current_student_requires_authenticated_session(self):
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)

    @patch("identity_service.verify_student_email")
    def test_verification_route_does_not_echo_token(self, verify):
        response = self.client.post("/api/v1/auth/verify-email", json={"token": "t" * 44})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("t" * 44, response.get_data(as_text=True))
        verify.assert_called_once()

    def test_password_reset_request_is_generic_for_unknown_accounts(self):
        with patch("identity_service.request_password_reset", return_value=None):
            response = self.client.post("/api/v1/auth/password-reset", json={
                "email": "unknown@example.com"
            })
        self.assertEqual(response.status_code, 202)
        self.assertIn("If an eligible account exists", response.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
