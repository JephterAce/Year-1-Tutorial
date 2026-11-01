import unittest
from pathlib import Path


class ProfileAssessmentMigrationTests(unittest.TestCase):
    def test_migration_adds_private_profile_defaults_and_consent(self):
        path = Path(__file__).resolve().parent / "migrations" / "004_student_profiles_and_assessments.sql"
        sql = path.read_text(encoding="utf-8")
        self.assertIn("DEFAULT 'private'", sql)
        self.assertIn("student_consent_records", sql)
        self.assertIn("optional_marketing", sql)
        self.assertIn("guardian_consent_status", sql)

    def test_assessment_answer_keys_are_stored_server_side(self):
        path = Path(__file__).resolve().parent / "migrations" / "004_student_profiles_and_assessments.sql"
        sql = path.read_text(encoding="utf-8")
        self.assertIn("answer_key JSONB NOT NULL", sql)
        self.assertIn("assessment_answers", sql)
        self.assertIn("assessment_attempts", sql)
        self.assertIn("assessment_attempt_questions", sql)

    def test_attempts_record_agreement_deadline_and_integrity_state(self):
        path = Path(__file__).resolve().parent / "migrations" / "004_student_profiles_and_assessments.sql"
        sql = path.read_text(encoding="utf-8")
        for required in ("agreement_recorded_at", "deadline_at", "policy_version",
                         "integrity_incidents", "integrity_review_required"):
            self.assertIn(required, sql)

    def test_only_deterministic_objective_question_types_are_allowed(self):
        path = Path(__file__).resolve().parent / "migrations" / "004_student_profiles_and_assessments.sql"
        sql = path.read_text(encoding="utf-8")
        self.assertIn("'single_choice','multiple_select','true_false','numeric','exact_text'", sql)
        self.assertNotIn("'essay'", sql)


if __name__ == "__main__":
    unittest.main()
