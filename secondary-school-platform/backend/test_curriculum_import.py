import unittest

from curriculum_import import validate_curriculum_row, validate_import, TARGET_VERSION


def valid_row(**overrides):
    row = {
        "class_level": "SS1",
        "subject_slug": "general-mathematics",
        "title": "Example topic from a verified source",
        "curriculum_version": TARGET_VERSION,
        "source_title": "NERDC SSS1 curriculum",
        "source_url": "https://nerdc.gov.ng/example",
        "source_kind": "official_nerdc",
        "source_section": "Section 2, page 14",
        "review_status": "approved",
        "reviewed_by": "Qualified subject teacher",
        "reviewed_at": "2026-11-02T10:00:00Z",
        "curriculum_evidence_note": "Topic wording checked against cited source.",
        "term_mapping_status": "official_term_allocation",
        "licence_status": "metadata_only",
        "learning_outcomes": ["Outcome transcribed from authorised source"],
    }
    row.update(overrides)
    return row


class CurriculumImportTests(unittest.TestCase):
    def test_accepts_target_version_metadata(self):
        result = validate_curriculum_row(valid_row())
        self.assertTrue(result.valid, result.errors)

    def test_rejects_legacy_or_unknown_version(self):
        result = validate_curriculum_row(valid_row(curriculum_version="legacy"))
        self.assertFalse(result.valid)

    def test_rejects_subject_outside_product_scope(self):
        result = validate_curriculum_row(valid_row(subject_slug="agricultural-science"))
        self.assertFalse(result.valid)

    def test_school_scheme_needs_name(self):
        result = validate_curriculum_row(valid_row(
            term_mapping_status="school_scheme_verified", source_kind="school_scheme"
        ))
        self.assertIn("school_scheme_name is required for school-scheme term mapping", result.errors)

    def test_official_term_claim_requires_nerdc_source(self):
        result = validate_curriculum_row(valid_row(source_kind="teacher_reference"))
        self.assertIn("official term allocation requires an official NERDC source", result.errors)

    def test_publication_fails_without_teacher_review(self):
        row = valid_row(review_status="mapped", reviewed_by="", reviewed_at="")
        result = validate_curriculum_row(row, for_publication=True)
        self.assertFalse(result.valid)
        self.assertTrue(any("approved review status" in error for error in result.errors))

    def test_term_pending_is_not_publishable_as_term_lesson(self):
        row = valid_row(term_mapping_status="school_scheme_required")
        result = validate_curriculum_row(row, for_publication=True)
        self.assertFalse(result.valid)

    def test_bulk_validation_reports_rows(self):
        result = validate_import([valid_row(), valid_row(class_level="SS4")])
        self.assertFalse(result["valid"])
        self.assertEqual(result["row_count"], 2)


if __name__ == "__main__":
    unittest.main()
