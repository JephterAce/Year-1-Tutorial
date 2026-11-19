import unittest
from assessment_reports import validate_report_payload, AssessmentReportError


class AssessmentReportValidationTests(unittest.TestCase):
    def test_valid_question_error_requires_question_reference(self):
        issue, details, question = validate_report_payload({
            "issue_type": "question_error", "details": "The answer options appear duplicated.",
            "question_id": "12345678-1234-4234-8234-123456789abc",
        })
        self.assertEqual(issue, "question_error")
        self.assertEqual(question, "12345678-1234-4234-8234-123456789abc")

    def test_question_error_without_question_is_rejected(self):
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({"issue_type": "question_error", "details": "This question is wrong."})

    def test_details_are_trimmed_and_length_limited(self):
        _, details, _ = validate_report_payload({
            "issue_type": "technical_issue", "details": "  The page froze after I saved my answer.  "
        })
        self.assertEqual(details, "The page froze after I saved my answer.")
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({"issue_type": "technical_issue", "details": "short"})

    def test_question_reference_must_be_a_uuid(self):
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({
                "issue_type": "question_error",
                "details": "The question has an incorrect answer.",
                "question_id": "question-123",
            })

    def test_unhashable_issue_type_is_rejected_cleanly(self):
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({"issue_type": [], "details": "Please investigate this report."})

    def test_only_known_issue_types_are_accepted(self):
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({"issue_type": "misconduct_finding", "details": "Please investigate this."})


if __name__ == "__main__":
    unittest.main()
