"""Authenticated, self-service JSON export of a student's own platform data.

Queries are strictly scoped by the authenticated student ID. Projections never
select password hashes, session/token data, provider payloads or answer keys.
The optional connection argument lets an approved bulk-export worker reuse one
repeatable-read, read-only database snapshot across every student in the job.
"""
from contextlib import nullcontext
from datetime import datetime, timezone

from database import connection


class StudentExportError(ValueError):
    pass


def _rows(conn, sql, student_id):
    return [dict(row) for row in conn.execute(sql, (student_id,)).fetchall()]


def build_student_export(student_id, conn=None):
    manager = connection() if conn is None else nullcontext(conn)
    with manager as db:
        student = db.execute(
            """SELECT id,email,display_name,username,class_level,bio,profile_visibility,
                      privacy_notice_version,guardian_consent_status,marketing_opt_in,
                      created_at,updated_at
               FROM students WHERE id=%s""",
            (student_id,),
        ).fetchone()
        if not student:
            raise StudentExportError("student_not_found")

        consents = _rows(db,
            """SELECT consent_type,policy_version,granted,recorded_at,withdrawn_at
               FROM student_consent_records WHERE student_id=%s ORDER BY recorded_at""",
            student_id)
        topic_progress = _rows(db,
            """SELECT p.topic_id,t.title AS topic_title,s.name AS subject,t.class_level,
                      p.last_accessed_at,p.completed_at,p.updated_at
               FROM student_topic_progress p JOIN topics t ON t.id=p.topic_id
               JOIN subjects s ON s.id=t.subject_id
               WHERE p.student_id=%s ORDER BY p.updated_at DESC""",
            student_id)
        media_progress = _rows(db,
            """SELECT lp.topic_id,t.title AS topic_title,lp.position_seconds,
                      lp.completed_at,lp.updated_at
               FROM lesson_progress lp JOIN topics t ON t.id=lp.topic_id
               WHERE lp.student_id=%s ORDER BY lp.updated_at DESC""",
            student_id)
        practice = _rows(db,
            """SELECT a.topic_id,t.title AS topic_title,a.question_id,q.prompt,
                      a.submitted_answer,a.is_correct,a.attempted_at
               FROM student_lesson_practice_attempts a
               JOIN topics t ON t.id=a.topic_id
               JOIN lesson_practice_questions q ON q.id=a.question_id
               WHERE a.student_id=%s ORDER BY a.attempted_at DESC""",
            student_id)
        assessments = _rows(db,
            """SELECT a.id AS attempt_id,a.assessment_id,d.title AS assessment_title,
                      a.assessment_version,a.status,a.question_count,a.score,a.maximum_score,
                      a.percentage,a.passed,a.started_at,a.submitted_at,a.graded_at,a.created_at
               FROM assessment_attempts a JOIN assessments d ON d.id=a.assessment_id
               WHERE a.student_id=%s ORDER BY a.created_at DESC""",
            student_id)
        assessment_answers = _rows(db,
            """SELECT aa.attempt_id,aa.question_id,aa.answer,aa.is_correct,
                      aa.awarded_points,aa.saved_at
               FROM assessment_answers aa JOIN assessment_attempts a ON a.id=aa.attempt_id
               WHERE a.student_id=%s ORDER BY aa.saved_at""",
            student_id)
        payments = _rows(db,
            """SELECT p.provider,p.provider_reference,p.amount_kobo,p.currency,p.status,
                      p.verified_at,p.created_at,t.title AS topic_title
               FROM payment_transactions p JOIN topics t ON t.id=p.topic_id
               WHERE p.student_id=%s ORDER BY p.created_at DESC""",
            student_id)
        entitlements = _rows(db,
            """SELECT e.topic_id,t.title AS topic_title,e.grant_reason,e.granted_at,e.revoked_at
               FROM entitlements e JOIN topics t ON t.id=e.topic_id
               WHERE e.student_id=%s ORDER BY e.granted_at DESC""",
            student_id)
        saved_lessons = _rows(db,
            """SELECT b.topic_id,t.title AS topic_title,s.name AS subject,t.class_level,b.created_at AS saved_at
               FROM student_saved_topics b JOIN topics t ON t.id=b.topic_id
               JOIN subjects s ON s.id=t.subject_id
               WHERE b.student_id=%s ORDER BY b.created_at DESC""",
            student_id)
        rights_requests = _rows(db,
            """SELECT request_type,status,request_note,resolution_note,created_at,updated_at,
                      reviewed_at,resolved_at
               FROM student_data_rights_requests WHERE student_id=%s ORDER BY created_at DESC""",
            student_id)

    def serialise(rows):
        return [{key: value.isoformat() if hasattr(value, "isoformat") else
                 (str(value) if value.__class__.__name__ in {"UUID", "Decimal"} else value)
                 for key, value in row.items()} for row in rows]

    return {
        "export_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "student": serialise([dict(student)])[0],
        "consents": serialise(consents),
        "topic_progress": serialise(topic_progress),
        "media_progress": serialise(media_progress),
        "lesson_practice_attempts": serialise(practice),
        "assessment_attempts": serialise(assessments),
        "assessment_answers": serialise(assessment_answers),
        "payments": serialise(payments),
        "entitlements": serialise(entitlements),
        "saved_lessons": serialise(saved_lessons),
        "data_rights_requests": serialise(rights_requests),
        "security_notice": "This export excludes credentials, session tokens, verification/reset tokens, provider payloads and assessment answer keys.",
    }
