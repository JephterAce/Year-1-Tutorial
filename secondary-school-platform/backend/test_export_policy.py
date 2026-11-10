import unittest
from export_policy import (
    ASSESSMENT_EXPORT_FIELDS, NEVER_EXPORT_FIELDS, STUDENT_EXPORT_FIELDS,
    filter_export_fields, validate_export_request,
)


class TestExportPolicy(unittest.TestCase):
    def test_individual_request_requires_uuid(self):
        with self.assertRaises(ValueError):
            validate_export_request({"scope": "individual", "format": "json"})
        request = validate_export_request({
            "scope": "individual", "format": "json",
            "student_id": "123e4567-e89b-12d3-a456-426614174000",
        })
        self.assertEqual(request.scope, "individual")

    def test_bulk_filters_are_validated_and_deduplicated(self):
        request = validate_export_request({
            "scope": "bulk", "format": "csv",
            "class_levels": ["SS2", "SS1", "SS2"],
            "subject_slugs": ["general-mathematics"],
        })
        self.assertEqual(request.class_levels, ("SS1", "SS2"))
        self.assertEqual(request.subject_slugs, ("general-mathematics",))

    def test_rejects_bulk_single_student_and_invalid_class(self):
        with self.assertRaises(ValueError):
            validate_export_request({
                "scope": "bulk", "format": "json",
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
            })
        with self.assertRaises(ValueError):
            validate_export_request({
                "scope": "bulk", "format": "json", "class_levels": ["SS4"],
            })

    def test_date_range_is_bounded(self):
        with self.assertRaises(ValueError):
            validate_export_request({
                "scope": "bulk", "format": "json",
                "date_from": "2024-01-01", "date_to": "2025-12-31",
            })

    def test_allowlist_never_includes_secrets_or_answer_keys(self):
        self.assertTrue(NEVER_EXPORT_FIELDS.isdisjoint(STUDENT_EXPORT_FIELDS))
        self.assertTrue(NEVER_EXPORT_FIELDS.isdisjoint(ASSESSMENT_EXPORT_FIELDS))
        rows = filter_export_fields([{
            "student_id": "s1", "email": "student@example.test",
            "password_hash": "do-not-export", "answer_key": "secret",
        }], STUDENT_EXPORT_FIELDS)
        self.assertEqual(rows, [{
            "student_id": "s1", "email": "student@example.test",
        }])


if __name__ == "__main__":
    unittest.main()
