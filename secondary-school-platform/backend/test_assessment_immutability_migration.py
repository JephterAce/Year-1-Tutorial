import unittest
from pathlib import Path


class AssessmentImmutabilityMigrationTests(unittest.TestCase):
    def test_attempt_questions_have_private_snapshot_columns(self):
        sql = (Path(__file__).resolve().parent / "migrations" /
               "008_assessment_immutability.sql").read_text(encoding="utf-8")
        for column in (
            "question_snapshot", "answer_key_snapshot", "points_snapshot",
            "numeric_tolerance_snapshot", "accepted_answers_snapshot",
        ):
            self.assertIn(column, sql)

    def test_published_assessment_and_question_mutations_are_blocked(self):
        sql = (Path(__file__).resolve().parent / "migrations" /
               "008_assessment_immutability.sql").read_text(encoding="utf-8")
        self.assertIn("assessments_immutable_after_publish", sql)
        self.assertIn("assessment_questions_immutable_after_publish", sql)
        self.assertIn("OLD.status = 'published'", sql)
        self.assertIn("Questions in published assessments are immutable", sql)

    def test_snapshot_comment_requires_server_side_capture_and_projection_exclusion(self):
        sql = (Path(__file__).resolve().parent / "migrations" /
               "008_assessment_immutability.sql").read_text(encoding="utf-8")
        self.assertIn("trusted attempt-start transaction", sql)
        self.assertIn("must never project answer_key_snapshot", sql)


if __name__ == "__main__":
    unittest.main()
