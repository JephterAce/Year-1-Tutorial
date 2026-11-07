"""Private, database-backed student bookmarks for published lesson topics."""
from database import connection


class SavedLessonError(ValueError):
    def __init__(self, code, status=400):
        super().__init__(code)
        self.code = code
        self.status = status


def list_saved_lessons(student_id):
    with connection() as conn:
        rows = conn.execute(
            """SELECT t.id,t.title,t.summary,t.class_level,s.name AS subject,
                      b.created_at
               FROM student_saved_topics b
               JOIN topics t ON t.id=b.topic_id
               JOIN subjects s ON s.id=t.subject_id
               WHERE b.student_id=%s AND t.status='published'
                 AND t.curriculum_status='published'
               ORDER BY b.created_at DESC LIMIT 100""",
            (student_id,),
        ).fetchall()
    return {"items": [{
        "topic_id": str(row["id"]),
        "title": row["title"],
        "summary": row["summary"],
        "class_level": row["class_level"],
        "subject": row["subject"],
        "saved_at": row["created_at"].isoformat() if row["created_at"] else None,
    } for row in rows]}


def save_lesson(student_id, topic_id):
    with connection() as conn:
        topic = conn.execute(
            """SELECT id FROM topics WHERE id=%s AND status='published'
               AND curriculum_status='published'""",
            (topic_id,),
        ).fetchone()
        if not topic:
            raise SavedLessonError("lesson_not_available", 404)
        inserted = conn.execute(
            """INSERT INTO student_saved_topics(student_id,topic_id)
               VALUES (%s,%s) ON CONFLICT (student_id,topic_id) DO NOTHING
               RETURNING topic_id""",
            (student_id, topic_id),
        ).fetchone()
    return {"saved": True, "already_saved": inserted is None}


def remove_saved_lesson(student_id, topic_id):
    with connection() as conn:
        removed = conn.execute(
            """DELETE FROM student_saved_topics
               WHERE student_id=%s AND topic_id=%s RETURNING topic_id""",
            (student_id, topic_id),
        ).fetchone()
    return {"saved": False, "removed": removed is not None}
