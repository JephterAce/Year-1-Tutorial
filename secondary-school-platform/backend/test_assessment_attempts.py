import unittest
from assessment_attempts import _public_question, POLICY_VERSION, BRIEFING
from assessment_policy import calculate_test_timing


class AssessmentAttemptContractTests(unittest.TestCase):
    def test_student_projection_never_contains_answer_key(self):
        row = {
            "question_id": "q-1", "display_order": 1, "points_snapshot": 2,
            "question_snapshot": {
                "question_type": "single_choice",
                "prompt": {"text": "Choose one"},
                "options": [{"id": "a", "text": "A", "is_correct": True, "answer_key": "secret"}],
                "answer_key": {"correct_option_id": "a"},
            },
        }
        projected = _public_question(row)
        self.assertEqual(projected["prompt"]["text"], "Choose one")
        self.assertNotIn("answer_key", projected)
        self.assertNotIn("answer_key_snapshot", projected)
        self.assertEqual(projected["options"], [{"id": "a", "text": "A"}])

    def test_time_exception_is_server_policy(self):
        self.assertEqual(calculate_test_timing(10).time_limit_seconds, 420)
        self.assertEqual(calculate_test_timing(20).time_limit_seconds, 720)

    def test_briefing_covers_server_timer_and_integrity_limits(self):
        briefing = " ".join(BRIEFING).lower()
        self.assertIn("server clock", briefing)
        self.assertIn("7 minutes", briefing)
        self.assertIn("not automatically treated as proven misconduct", briefing)
        self.assertIn("screenshots", briefing)

    def test_policy_version_is_explicit(self):
        self.assertTrue(POLICY_VERSION.startswith("learnwise-test-briefing-v"))


if __name__ == "__main__":
    unittest.main()
