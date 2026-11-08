import os
import unittest
from unittest.mock import patch

from app import app
from admin_policy import AdminPrincipal


class StagingStorageDiagnosticRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.flags = {"APP_ENV": "staging", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "true"}
        self.owner = {
            "admin_id": "owner-id", "email": "owner@example.test", "role": "owner",
            "principal": AdminPrincipal("owner-id", "owner", True),
        }

    def test_storage_diagnostic_is_hidden_when_flag_is_disabled(self):
        with patch.dict(os.environ, {"APP_ENV": "staging", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "false"}):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 404)

    def test_storage_diagnostic_is_hidden_outside_staging(self):
        with patch.dict(os.environ, {"APP_ENV": "production", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "true"}):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 404)

    def test_storage_diagnostic_requires_admin_session_and_csrf(self):
        with patch.dict(os.environ, self.flags), patch("app._current_admin", return_value=None):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 401)

    def test_storage_diagnostic_rejects_request_body(self):
        with patch.dict(os.environ, self.flags), patch("app._current_admin", return_value=self.owner):
            response = self.client.post("/api/v1/admin/diagnostics/storage", json={"bucket": "override"})
        self.assertEqual(response.status_code, 400)

    def test_storage_diagnostic_records_synthetic_results(self):
        result = {
            "passed": True,
            "results": {
                "audio": {"configured": True, "passed": True, "upload": True, "retrieval": True,
                          "checksum_match": True, "unsigned_access_denied": True, "deletion": True,
                          "sha256": "a" * 64},
                "r2_exports": {"configured": True, "passed": True, "upload": True, "retrieval": True,
                               "checksum_match": True, "unsigned_access_denied": True, "deletion": True,
                               "sha256": "b" * 64},
            },
        }
        with patch.dict(os.environ, self.flags), \
             patch("app._current_admin", return_value=self.owner), \
             patch("admin_auth.reserve_admin_storage_diagnostic"), \
             patch("storage_acceptance.run_private_storage_acceptance", return_value=result), \
             patch("admin_auth.record_admin_audit") as audit:
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["passed"])
        audit.assert_called_once()
        self.assertNotIn("secret_access_key", str(audit.call_args))

    def test_storage_diagnostic_returns_503_if_a_bucket_fails(self):
        result = {"passed": False, "results": {
            "audio": {"configured": True, "passed": False, "failure_class": "EndpointConnectionError"},
            "r2_exports": {"configured": True, "passed": True},
        }}
        with patch.dict(os.environ, self.flags), \
             patch("app._current_admin", return_value=self.owner), \
             patch("admin_auth.reserve_admin_storage_diagnostic"), \
             patch("storage_acceptance.run_private_storage_acceptance", return_value=result), \
             patch("admin_auth.record_admin_audit"):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.get_json()["passed"])


if __name__ == "__main__":
    unittest.main()
