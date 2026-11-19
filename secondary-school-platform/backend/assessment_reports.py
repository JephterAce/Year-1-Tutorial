"""Student-submitted assessment issue reports and integrity appeals."""
from uuid import UUID

from database import connection

ISSUE_TYPES = frozenset({"integrity_appeal", "question_error", "technical_issue"})


class AssessmentReportError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def validate_report_payload(payload):
    if not isinstance(payload, dict):
        raise AssessmentReportError("invalid_report", "A report object is required.")
    issue_type = payload.get("issue_type")
    if not isinstance(issue_type, str) or issue_type not in ISSUE_TYPES:
        raise AssessmentReportError("invalid_issue_type", "Choose a supported report type.")
    details = payload.get("details")
    if not isinstance(details, str):
        raise AssessmentReportError("invalid_details", "Describe the issue.")
    details = " ".join(details.split())
    if not 10 <= len(details) <= 2000:
        raise AssessmentReportError("invalid_details", "Details must be 10–2,000 characters.")
    question_id = payload.get("question_id")
    if issue_type == "question_error" and not question_id:
        raise AssessmentReportError("question_required", "Select the question with the problem.")
    if question_id is not None:
        try:
            question_id = str(UUID(question_id))
        except (TypeError, ValueError, AttributeError):
            raise AssessmentReportError("invalid_question", "The question reference is invalid.") from None
    return issue_type, details, question_id


def submit_assessment_report(student_id, attempt_id, payload):
    issue_type, details, question_id = validate_report_payload(payload)
    with connection() as conn:
        attempt = conn.execute(
            "SELECT id,status FROM assessment_attempts WHERE id=%s AND student_id=%s FOR UPDATE",
            (attempt_id, student_id),
        ).fetchone()
        if not attempt:
            raise AssessmentReportError("not_found", "Assessment attempt not found.", 404)
        if issue_type == "integrity_appeal" and attempt["status"] != "terminated_integrity":
            raise AssessmentReportError(
                "appeal_not_applicable", "This attempt is not awaiting an integrity appeal.", 409
            )
        if question_id:
            belongs = conn.execute(
                """SELECT 1 FROM assessment_attempt_questions
                   WHERE attempt_id=%s AND question_id=%s""",
                (attempt_id, question_id),
            ).fetchone()
            if not belongs:
                raise AssessmentReportError("invalid_question", "That question is not part of this attempt.")
        count = conn.execute(
            "SELECT count(*) AS n FROM assessment_issue_reports WHERE attempt_id=%s AND student_id=%s",
            (attempt_id, student_id),
        ).fetchone()["n"]
        if count >= 5:
            raise AssessmentReportError("report_limit", "The report limit for this attempt has been reached.", 429)
        report = conn.execute(
            """INSERT INTO assessment_issue_reports
               (attempt_id,student_id,question_id,issue_type,details)
               VALUES (%s,%s,%s,%s,%s) RETURNING id,issue_type,status,created_at""",
            (attempt_id, student_id, question_id, issue_type, details),
        ).fetchone()
        return {"id": str(report["id"]), "issue_type": report["issue_type"],
                "status": report["status"], "created_at": report["created_at"].isoformat()}


def list_my_assessment_reports(student_id, attempt_id):
    with connection() as conn:
        attempt = conn.execute(
            "SELECT 1 FROM assessment_attempts WHERE id=%s AND student_id=%s",
            (attempt_id, student_id),
        ).fetchone()
        if not attempt:
            raise AssessmentReportError("not_found", "Assessment attempt not found.", 404)
        rows = conn.execute(
            """SELECT id,issue_type,question_id,status,created_at,reviewed_at
               FROM assessment_issue_reports
               WHERE attempt_id=%s AND student_id=%s ORDER BY created_at DESC""",
            (attempt_id, student_id),
        ).fetchall()
        return [{**dict(row), "id": str(row["id"]),
                 "question_id": str(row["question_id"]) if row["question_id"] else None,
                 "created_at": row["created_at"].isoformat(),
                 "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] else None}
                for row in rows]
