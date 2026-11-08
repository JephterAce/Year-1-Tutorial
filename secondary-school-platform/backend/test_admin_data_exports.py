import unittest
from unittest.mock import patch

from admin_policy import AdminPrincipal


class AdminDataExportRouteTests(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()
        self.admin = {
            "principal": AdminPrincipal("11111111-1111-4111-8111-111111111111", "owner", True),
            "admin_id": "11111111-1111-4111-8111-111111111111",
            "email": "owner@example.test",
            "role": "owner",
        }

    def test_export_queue_requires_authorised_admin(self):
        with patch("admin_data_exports._admin", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.get("/api/v1/admin/data-exports")
        self.assertEqual(response.status_code, 401)

    def test_bulk_export_requires_narrow_scope(self):
        with patch("admin_data_exports._admin", return_value=(self.admin, None)):
            response = self.client.post(
                "/api/v1/admin/data-exports",
                json={"scope": "bulk", "format": "json", "class_levels": [], "confirm_bulk": True},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "bulk_export_requires_a_class_or_date_filter")

    def test_bulk_export_requires_explicit_confirmation(self):
        with patch("admin_data_exports._admin", return_value=(self.admin, None)):
            response = self.client.post(
                "/api/v1/admin/data-exports",
                json={"scope": "bulk", "format": "json", "class_levels": ["SS1"]},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "bulk_export_confirmation_required")

    def test_subject_scoped_bulk_export_fails_closed_until_implemented(self):
        with patch("admin_data_exports._admin", return_value=(self.admin, None)):
            response = self.client.post(
                "/api/v1/admin/data-exports",
                json={"scope": "bulk", "format": "json", "class_levels": ["SS1"],
                      "subject_slugs": ["biology"], "confirm_bulk": True},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "subject_scoped_bulk_export_not_supported")

    def test_approval_and_download_validate_identifiers_before_database_access(self):
        with patch("admin_data_exports._admin", return_value=(self.admin, None)):
            approved = self.client.post("/api/v1/admin/data-exports/not-a-uuid/approve", json={})
            downloaded = self.client.get("/api/v1/admin/data-exports/not-a-uuid/download")
        self.assertEqual(approved.status_code, 400)
        self.assertEqual(downloaded.status_code, 400)

    def test_approval_requires_csrf(self):
        with patch("admin_data_exports._admin", return_value=(None, ({"error": "csrf_failed"}, 401))):
            response = self.client.post(
                "/api/v1/admin/data-exports/123e4567-e89b-12d3-a456-426614174000/approve",
                json={},
            )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
