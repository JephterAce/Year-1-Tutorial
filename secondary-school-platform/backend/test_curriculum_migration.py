import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CurriculumMigrationContractTests(unittest.TestCase):
    def test_version_and_cohort_tables_exist(self):
        sql = (ROOT / "backend" / "migrations" / "009_curriculum_versioning_and_review.sql").read_text()
        self.assertIn("CREATE TABLE IF NOT EXISTS curriculum_versions", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS curriculum_cohort_assignments", sql)
        self.assertIn("pending_official_confirmation", sql)
        self.assertIn("nerdc_ssec_2025", sql)

    def test_term_can_remain_unassigned(self):
        sql = (ROOT / "backend" / "migrations" / "009_curriculum_versioning_and_review.sql").read_text()
        self.assertIn("ALTER COLUMN term_id DROP NOT NULL", sql)

    def test_published_catalogue_requires_approved_evidence(self):
        database = (ROOT / "backend" / "database.py").read_text()
        self.assertIn("t.curriculum_status = 'published'", database)
        self.assertIn("cv.version_code = 'nerdc_ssec_2025'", database)
        self.assertIn("csr.verification_status = 'approved'", database)
        self.assertIn("JOIN curriculum_source_records csr", database)

    def test_workflow_forbids_guessed_term_mapping(self):
        workflow = (ROOT / "CURRICULUM_WORKFLOW.md").read_text()
        self.assertIn("do not guess a term", workflow.lower())
        self.assertIn("pending_official_confirmation", workflow)


if __name__ == "__main__":
    unittest.main()
