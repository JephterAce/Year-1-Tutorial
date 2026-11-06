"""Entitlement-checked lesson notes, practice and topic progress."""
from decimal import Decimal
from database import connection
from psycopg.types.json import Jsonb


class LessonContentError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def _require_entitlement(conn, student_id, topic_id):
    row = conn.execute(
        """SELECT 1 FROM entitlements
           WHERE student_id=%s AND topic_id=%s AND revoked_at IS NULL LIMIT 1""",
        (student_id, topic_id),
    ).fetchone()
    if not row:
        raise LessonContentError("entitlement_required", "Unlock this lesson to access its notes and practice.", 402)


def get_lesson_content(student_id, topic_id):
    with connection() as conn:
        _require_entitlement(conn, student_id, topic_id)
        row = conn.execute(
            """SELECT c.id,c.version,c.content_json
               FROM topic_lesson_content c
               JOIN topics t ON t.id=c.topic_id
               WHERE c.topic_id=%s AND c.review_status='approved'
                 AND t.status='published' AND t.curriculum_status='published'
               ORDER BY c.version DESC LIMIT 1""",
            (topic_id,),
        ).fetchone()
        if not row:
            raise LessonContentError("lesson_content_unavailable", "Reviewed lesson notes are not available yet.", 404)
        questions = conn.execute(
            """SELECT id,question_type,prompt,options,points,sort_order
               FROM lesson_practice_questions
               WHERE topic_id=%s AND lesson_content_id=%s AND review_status='approved'
               ORDER BY sort_order,id""",
            (topic_id, row["id"]),
        ).fetchall()
    return {
        "content_id": str(row["id"]),
        "version": row["version"],
        "content": row["content_json"],
        "practice": [{
            "id": str(q["id"]), "type": q["question_type"], "prompt": q["prompt"],
            "options": q["options"], "points": str(q["points"]),
        } for q in questions],
    }


def check_practice_answer(student_id, topic_id, question_id, answer):
    if not isinstance(answer, (str, int, float, bool)):
        raise LessonContentError("invalid_answer", "Enter a valid answer.")
    if isinstance(answer, str) and len(answer) > 100:
        raise LessonContentError("invalid_answer", "Your answer is too long.")
    with connection() as conn:
        _require_entitlement(conn, student_id, topic_id)
        row = conn.execute(
            """SELECT q.question_type,q.answer_key,q.explanation
               FROM lesson_practice_questions q
               JOIN topic_lesson_content c ON c.id=q.lesson_content_id
               JOIN topics t ON t.id=q.topic_id
               WHERE q.id=%s AND q.topic_id=%s AND q.review_status='approved'
                 AND c.review_status='approved'
                 AND t.status='published' AND t.curriculum_status='published'""",
            (question_id, topic_id),
        ).fetchone()
        if not row:
            raise LessonContentError("practice_unavailable", "This practice question is unavailable.", 404)
    expected = row["answer_key"].get("value") if isinstance(row["answer_key"], dict) else row["answer_key"]
    if row["question_type"] == "numeric":
        if isinstance(answer, bool) or not isinstance(answer, (int, float, str)):
            raise LessonContentError("invalid_answer", "Enter a numeric answer.")
        try:
            submitted_number, expected_number = Decimal(str(answer)), Decimal(str(expected))
            correct = submitted_number.is_finite() and expected_number.is_finite() and submitted_number == expected_number
        except Exception:
            correct = False
    else:
        correct = str(answer).strip().casefold() == str(expected).strip().casefold()
    with connection() as conn:
        conn.execute(
            """INSERT INTO student_lesson_practice_attempts
                 (student_id,topic_id,question_id,submitted_answer,is_correct)
               VALUES (%s,%s,%s,%s,%s)""",
            (student_id,topic_id,question_id,Jsonb({"value":answer}),correct),
        )
    return {"correct": correct, "explanation": row["explanation"]}


def mark_topic_complete(student_id, topic_id):
    with connection() as conn:
        _require_entitlement(conn, student_id, topic_id)
        content = conn.execute(
            """SELECT c.id FROM topic_lesson_content c
               JOIN topics t ON t.id=c.topic_id
               WHERE c.topic_id=%s AND c.review_status='approved'
                 AND t.status='published' AND t.curriculum_status='published'
               ORDER BY c.version DESC LIMIT 1""",
            (topic_id,),
        ).fetchone()
        if not content:
            raise LessonContentError("lesson_content_unavailable", "Reviewed lesson notes are not available yet.", 404)
        conn.execute(
            """INSERT INTO student_topic_progress
                 (student_id,topic_id,lesson_content_id,last_accessed_at,completed_at)
               VALUES (%s,%s,%s,now(),now())
               ON CONFLICT(student_id,topic_id) DO UPDATE SET
                 lesson_content_id=EXCLUDED.lesson_content_id,
                 last_accessed_at=now(),completed_at=COALESCE(student_topic_progress.completed_at,now()),
                 updated_at=now()""",
            (student_id, topic_id, content["id"]),
        )
    return {"completed": True}
