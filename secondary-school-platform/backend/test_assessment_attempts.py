import unittest
from assessment_attempts import _public_question, POLICY_VERSION
from assessment_policy import calculate_test_timing


class AssessmentAttemptContractTests(unittest.TestCase):
    def test_student_projection_never_contains_answer_key(self):
        row = {
            "question_id": "q-1", "display_order": 1, "points_snapshot": 2,
            "question_snapshot": {
                "question_type": "single_choice",
                "prompt": {"text": "Choose one"},
                "options": [{"id": "a", "text": "A"}],
                "answer_key": {"correct_option_id": "a"},
            },
        }
        projected = _public_question(row)
        self.assertEqual(projected["prompt"]["text"], "Choose one")
        self.assertNotIn("answer_key", projected)
        self.assertNotIn("answer_key_snapshot", projected)

    def test_time_exception_is_server_policy(self):
        self.assertEqual(calculate_test_timing(10).time_limit_seconds, 420)
        self.assertEqual(calculate_test_timing(20).time_limit_seconds, 720)

    def test_policy_version_is_explicit(self):
        self.assertTrue(POLICY_VERSION.startswith("learnwise-test-briefing-v"))


if __name__ == "__main__":
    unittest.main()
