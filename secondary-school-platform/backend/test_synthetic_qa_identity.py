import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app import app
from admin_policy import AdminPrincipal


class SyntheticQAIdentityRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.staging_flags = {
            "APP_ENV": "staging",
            "STAGING_QA_IDENTITY_ENABLED": "true",
            "STUDENT_REGISTRATION_ENABLED": "false",
        }

    def owner_session(self):
        return {
            "admin_id": "owner-id",
            "email": "owner@example.test",
            "role": "owner",
            "principal": AdminPrincipal("owner-id", "owner", True),
        }

    def test_provisioning_is_not_found_outside_explicit_staging_opt_in(self):
        with patch.dict(os.environ, {"APP_ENV": "production", "STAGING_QA_IDENTITY_ENABLED": "true"}):
            response = self.client.post("/api/v1/admin/qa-identities")
        self.assertEqual(response.status_code, 404)

    def test_provisioning_requires_owner_session_and_csrf(self):
        with patch.dict(os.environ, self.staging_flags), patch("app._current_admin", return_value=None):
            response = self.client.post("/api/v1/admin/qa-identities")
        self.assertEqual(response.status_code, 401)

    def test_provisioning_rejects_request_body_to_prevent_recipient_override(self):
        with patch.dict(os.environ, self.staging_flags), patch("app._current_admin", return_value=self.owner_session()):
            response = self.client.post("/api/v1/admin/qa-identities", json={"email": "other@example.test"})
        self.assertEqual(response.status_code, 400)

    def test_provisioning_sends_only_to_configured_mailbox_and_never_returns_credentials(self):
        student = {
            "id": "synthetic-id",
            "email": "qa@example.test",
            "synthetic_qa_expires_at": datetime(2026, 11, 9, tzinfo=timezone.utc),
        }
        provisioned = {
            "student": student,
            "verification_token": "raw-verification-token-never-return",
            "temporary_password": "temporary-password-never-return",
        }
        with patch.dict(os.environ, self.staging_flags), \
             patch("app._current_admin", return_value=self.owner_session()), \
             patch("identity_service.provision_synthetic_qa_student", return_value=provisioned), \
             patch("identity_email.send_synthetic_qa_invite") as send, \
             patch("admin_auth.record_admin_audit"):
            response = self.client.post("/api/v1/admin/qa-identities")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.get_json()["synthetic_qa"])
        self.assertNotIn("raw-verification-token-never-return", response.get_data(as_text=True))
        self.assertNotIn("temporary-password-never-return", response.get_data(as_text=True))
        send.assert_called_once_with(
            "qa@example.test", "raw-verification-token-never-return",
            "temporary-password-never-return",
        )

    def test_synthetic_session_can_confirm_identity_but_cannot_start_assessments(self):
        synthetic_session = {
            "student_id": "synthetic-id",
            "email": "qa@example.test",
            "username": "qa_test",
            "display_name": "Synthetic QA Student",
            "class_level": "SS1",
            "is_synthetic_qa": True,
            "synthetic_qa_expires_at": datetime(2026, 11, 9, tzinfo=timezone.utc),
            "csrf_token_hash": "unused",
            "session_row_id": "session-row",
        }
        with patch("identity_service.authenticate_session", return_value=synthetic_session), \
             patch("identity_service.validate_csrf", return_value=True):
            self.client.set_cookie("learnwise_session", "s" * 44)
            identity = self.client.get("/api/v1/auth/me")
            assessment = self.client.post("/api/v1/assessments/assessment-id/attempts", json={})
        self.assertEqual(identity.status_code, 200)
        self.assertTrue(identity.get_json()["student"]["is_synthetic_qa"])
        self.assertEqual(assessment.status_code, 401)

    def test_public_registration_remains_disabled_in_staging(self):
        with patch.dict(os.environ, self.staging_flags):
            response = self.client.post("/api/v1/auth/register", json={})
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
