import unittest
from decimal import Decimal

from assessment_grading import GradingError, grade_answer, grade_attempt


class AssessmentGradingTests(unittest.TestCase):
    def test_single_choice(self):
        q = {"question_type": "single_choice", "answer_key": {"correct_option_id": "b"}, "points": 2}
        self.assertTrue(grade_answer(q, "b")["is_correct"])
        self.assertFalse(grade_answer(q, "a")["is_correct"])

    def test_multiple_select_requires_exact_set_and_rejects_duplicates(self):
        q = {"question_type": "multiple_select", "answer_key": {"correct_option_ids": ["a", "c"]}}
        self.assertTrue(grade_answer(q, ["c", "a"])["is_correct"])
        self.assertFalse(grade_answer(q, ["a"])["is_correct"])
        self.assertFalse(grade_answer(q, ["a", "a", "c"])["is_correct"])

    def test_true_false_is_strict_boolean(self):
        q = {"question_type": "true_false", "answer_key": {"correct": True}}
        self.assertTrue(grade_answer(q, True)["is_correct"])
        self.assertFalse(grade_answer(q, "true")["is_correct"])

    def test_numeric_tolerance_and_non_finite_values(self):
        q = {"question_type": "numeric", "answer_key": {"value": "3.14"},
             "numeric_tolerance": "0.01", "points": 1}
        self.assertTrue(grade_answer(q, "3.149")["is_correct"])
        self.assertFalse(grade_answer(q, "3.16")["is_correct"])
        self.assertFalse(grade_answer(q, "NaN")["is_correct"])

    def test_exact_text_normalises_case_and_whitespace(self):
        q = {"question_type": "exact_text", "accepted_answers": ["cell membrane", "plasma membrane"],
             "answer_key": {}}
        self.assertTrue(grade_answer(q, "  CELL   membrane ")["is_correct"])
        self.assertFalse(grade_answer(q, "cell wall")["is_correct"])

    def test_attempt_totals_and_percentage(self):
        items = [
            ({"question_type": "single_choice", "answer_key": {"correct_option_id": "a"}, "points": 2}, "a"),
            ({"question_type": "true_false", "answer_key": {"correct": True}, "points": 1}, False),
        ]
        result = grade_attempt(items)
        self.assertEqual(result["score"], Decimal("2"))
        self.assertEqual(result["maximum_score"], Decimal("3"))
        self.assertEqual(result["percentage"], Decimal("66.67"))
        self.assertNotIn("answer_key", result)

    def test_invalid_question_definitions_fail_closed(self):
        with self.assertRaises(GradingError):
            grade_answer({"question_type": "essay", "answer_key": {}}, "text")
        with self.assertRaises(GradingError):
            grade_answer({"question_type": "numeric", "answer_key": {"value": "2"},
                          "numeric_tolerance": "-1"}, "2")


if __name__ == "__main__":
    unittest.main()
