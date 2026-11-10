import unittest
from unittest.mock import patch

from admin_assessments import _question_payload, AssessmentInputError


class AssessmentQuestionValidationTests(unittest.TestCase):
    def test_single_choice_requires_correct_option_from_declared_options(self):
        payload = _question_payload({
            "question_type": "single_choice",
            "prompt": "Which particle has a negative charge?",
            "options": [
                {"id": "electron", "text": "Electron"},
                {"id": "proton", "text": "Proton"},
            ],
            "answer_key": {"correct_option_id": "electron"},
        })
        self.assertEqual(payload["question_type"], "single_choice")
        self.assertEqual(payload["answer_key"]["correct_option_id"], "electron")

    def test_single_choice_rejects_answer_key_not_in_options(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "single_choice",
                "prompt": "Select the correct answer",
                "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
                "answer_key": {"correct_option_id": "secret"},
            })

    def test_multiple_select_rejects_duplicate_correct_options(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "multiple_select",
                "prompt": "Select all correct statements",
                "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
                "answer_key": {"correct_option_ids": ["a", "a"]},
            })

    def test_multiple_select_rejects_non_string_option_ids(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "multiple_select",
                "prompt": "Select all correct statements",
                "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
                "answer_key": {"correct_option_ids": [{"unexpected": "object"}]},
            })

    def test_true_false_requires_boolean_answer(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "true_false",
                "prompt": "Water is a compound.",
                "answer_key": {"correct": "true"},
            })

    def test_numeric_requires_finite_answer_and_nonnegative_tolerance(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "numeric",
                "prompt": "Calculate 2 + 2.",
                "answer_key": {"value": "NaN"},
                "numeric_tolerance": -1,
            })

    def test_exact_text_requires_accepted_answers(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "exact_text",
                "prompt": "Name the process by which plants make food.",
                "answer_key": {},
                "accepted_answers": [],
            })

    def test_points_must_be_positive_and_bounded(self):
        with self.assertRaises(AssessmentInputError):
            _question_payload({
                "question_type": "true_false",
                "prompt": "A valid true or false question.",
                "answer_key": {"correct": True},
                "points": 0,
            })


class AssessmentAuthoringRouteSecurityTests(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_list_requires_admin_session(self):
        with patch("admin_assessments._authorise", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.get("/api/v1/admin/assessments")
        self.assertEqual(response.status_code, 401)

    def test_create_requires_admin_session_and_csrf(self):
        with patch("admin_assessments._authorise", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.post("/api/v1/admin/assessments", json={})
        self.assertEqual(response.status_code, 401)

    def test_publish_requires_admin_session_and_csrf(self):
        with patch("admin_assessments._authorise", return_value=(None, ({"error": "unauthenticated"}, 401))):
            response = self.client.post(
                "/api/v1/admin/assessments/00000000-0000-0000-0000-000000000001/publish",
                json={},
            )
        self.assertEqual(response.status_code, 401)



class AssessmentAuthoringUiTests(unittest.TestCase):
    def test_authoring_page_uses_protected_admin_api_and_csrf(self):
        from pathlib import Path
        page = Path(__file__).resolve().parents[1] / "admin" / "assessments.html"
        source = page.read_text(encoding="utf-8")
        for marker in (
            "/api/v1/admin/assessment-subjects",
            "/api/v1/admin/assessments",
            "X-CSRF-Token",
            "/questions",
            "/publish",
            "Published assessments are immutable",
            'href="#main">Skip to main content',
            "@media(max-width:680px)",
        ):
            self.assertIn(marker, source)

    def test_assessment_detail_projection_does_not_select_answer_keys(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parent / "admin_assessments.py").read_text(encoding="utf-8")
        self.assertIn("SELECT id,question_type,prompt,options,explanation,points,sort_order", source)
        self.assertNotIn("SELECT id,question_type,prompt,options,answer_key", source)


if __name__ == "__main__":
    unittest.main()
