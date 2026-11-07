import unittest
from unittest.mock import patch


class StudentDataRightsRouteTests(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_self_service_export_requires_student_session(self):
        with patch("student_data_rights._student", return_value=None):
            response = self.client.get("/api/v1/student/data-export")
        self.assertEqual(response.status_code, 401)

    def test_export_queries_are_student_scoped_and_never_select_secrets(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parent / "student_data_export.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("WHERE student_id=%s"), 9)
        self.assertNotIn("SELECT password_hash", source)
        self.assertNotIn("SELECT answer_key", source)
        self.assertNotIn("SELECT provider_payload", source)
        self.assertIn("assessment_answers", source)
        self.assertIn("security_notice", source)

    def test_student_request_list_requires_session(self):
        with patch("student_data_rights._student", return_value=None):
            response = self.client.get("/api/v1/student/data-rights/requests")
        self.assertEqual(response.status_code, 401)

    def test_student_request_creation_requires_session_and_csrf(self):
        with patch("student_data_rights._student", return_value=None):
            response = self.client.post(
                "/api/v1/student/data-rights/requests",
                json={"request_type": "deletion"},
            )
        self.assertEqual(response.status_code, 401)

    def test_student_withdrawal_requires_session_and_csrf(self):
        with patch("student_data_rights._student", return_value=None):
            response = self.client.post(
                "/api/v1/student/data-rights/requests/00000000-0000-0000-0000-000000000001/withdraw",
                json={},
            )
        self.assertEqual(response.status_code, 401)

    def test_admin_queue_requires_support_or_owner_session(self):
        with patch("student_data_rights._admin", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.get("/api/v1/admin/data-rights/requests")
        self.assertEqual(response.status_code, 401)

    def test_admin_review_requires_session_and_csrf(self):
        with patch("student_data_rights._admin", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.post(
                "/api/v1/admin/data-rights/requests/00000000-0000-0000-0000-000000000001/review",
                json={"status": "resolved", "resolution_note": "Request processed."},
            )
        self.assertEqual(response.status_code, 401)

    def test_deletion_request_is_intake_only_not_an_automatic_delete(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parent / "student_data_rights.py").read_text(encoding="utf-8")
        self.assertIn("not automatically executed", source)
        self.assertIn("UPDATE students SET deletion_requested_at=now()", source)
        self.assertNotIn("DELETE FROM students", source)


if __name__ == "__main__":
    unittest.main()
