import unittest
from unittest.mock import patch

from admin_policy import AdminPrincipal
from admin_assessment_reviews import list_review_queue, review_report


class AdminAssessmentReviewPolicyTests(unittest.TestCase):
    def test_editor_cannot_read_review_queue(self):
        with self.assertRaises(PermissionError):
            list_review_queue(AdminPrincipal("admin-1", "editor", True))

    def test_inactive_reviewer_cannot_read_queue(self):
        with self.assertRaises(PermissionError):
            list_review_queue(AdminPrincipal("admin-1", "reviewer", False))

    def test_reviewer_can_read_queue(self):
        with patch("admin_assessment_reviews.connection") as connection:
            connection.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []
            self.assertEqual(list_review_queue(AdminPrincipal("admin-1", "reviewer", True)), [])

    def test_support_cannot_read_sensitive_queue(self):
        with self.assertRaises(PermissionError):
            list_review_queue(AdminPrincipal("admin-1", "support", True))

    def test_invalid_transition_is_rejected(self):
        principal = AdminPrincipal("admin-1", "reviewer", True)
        fake = {"id": "12345678-1234-4234-8234-123456789abc",
                "status": "resolved", "issue_type": "question_error"}
        with patch("admin_assessment_reviews.connection") as connection:
            connection.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = fake
            with self.assertRaises(ValueError):
                review_report(principal, fake["id"], "under_review", "Reviewed this issue carefully.")

    def test_invalid_note_is_rejected_before_database_access(self):
        principal = AdminPrincipal("admin-1", "reviewer", True)
        with patch("admin_assessment_reviews.connection") as connection:
            with self.assertRaises(ValueError):
                review_report(principal, "12345678-1234-4234-8234-123456789abc",
                              "resolved", "short")
            connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
