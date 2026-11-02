import unittest
from assessment_reports import validate_report_payload, AssessmentReportError


class AssessmentReportValidationTests(unittest.TestCase):
    def test_valid_question_error_requires_question_reference(self):
        issue, details, question = validate_report_payload({
            "issue_type": "question_error", "details": "The answer options appear duplicated.",
            "question_id": "question-123",
        })
        self.assertEqual(issue, "question_error")
        self.assertEqual(question, "question-123")

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

    def test_only_known_issue_types_are_accepted(self):
        with self.assertRaises(AssessmentReportError):
            validate_report_payload({"issue_type": "misconduct_finding", "details": "Please investigate this."})


if __name__ == "__main__":
    unittest.main()
