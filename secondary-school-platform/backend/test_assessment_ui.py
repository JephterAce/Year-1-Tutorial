import unittest
from pathlib import Path


class AssessmentUiContractTests(unittest.TestCase):
    def test_student_assessment_page_uses_server_deadline_and_csrf(self):
        page = (Path(__file__).parents[1] / "frontend" / "assessment.html").read_text()
        self.assertIn("/api/v1/assessments", page)
        self.assertIn("/api/v1/assessment-attempts/", page)
        self.assertIn("X-CSRF-Token", page)
        self.assertIn("deadline_at", page)
        self.assertIn("visibility_hidden", page)
        self.assertIn("fullscreen_exit", page)
        self.assertIn("integrity_review_required", page)
        self.assertIn("requestFullscreen", page)

    def test_student_page_never_embeds_answer_keys(self):
        page = (Path(__file__).parents[1] / "frontend" / "assessment.html").read_text()
        self.assertNotIn("answer_key_snapshot", page)
        self.assertNotIn("correct_option_id", page)


if __name__ == "__main__":
    unittest.main()
