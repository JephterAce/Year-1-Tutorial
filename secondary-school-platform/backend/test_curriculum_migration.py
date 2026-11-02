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

    def test_database_publication_guard_checks_source_and_review(self):
        sql = (ROOT / "backend" / "migrations" / "010_curriculum_publication_guard.sql").read_text()
        self.assertIn("CREATE TRIGGER topics_curriculum_publication_guard", sql)
        self.assertIn("source_row.verification_status <> 'approved'", sql)
        self.assertIn("source_row.class_level <> NEW.class_level", sql)
        self.assertIn("curriculum_approved_by", sql)
        self.assertIn("school_scheme_name", sql)

    def test_term_mapping_constraint_accepts_unassigned_state(self):
        sql = (ROOT / "backend" / "migrations" / "010_curriculum_publication_guard.sql").read_text()
        self.assertIn("'not_assigned'", sql)

    def test_workflow_forbids_guessed_term_mapping(self):
        workflow = (ROOT / "CURRICULUM_WORKFLOW.md").read_text()
        self.assertIn("do not guess a term", workflow.lower())
        self.assertIn("pending_official_confirmation", workflow)

if __name__ == "__main__":
    unittest.main()

    def test_published_source_and_version_cannot_be_mutated(self):
        sql = (ROOT / "backend" / "migrations" / "011_curriculum_source_immutability.sql").read_text()
        self.assertIn("curriculum_source_published_immutability", sql)
        self.assertIn("BEFORE UPDATE OR DELETE ON curriculum_source_records", sql)
        self.assertIn("curriculum_version_published_immutability", sql)
        self.assertIn("NEW.status IS DISTINCT FROM OLD.status", sql)
        self.assertIn("curriculum_source_record_id = source_id", sql)
        self.assertIn("create and review a replacement source first", sql)

