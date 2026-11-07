import unittest
from unittest.mock import patch

import student_saved_lessons as saved
from student_saved_lessons import SavedLessonError


class Cursor:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class Connection:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        if self.responses:
            return self.responses.pop(0)
        return Cursor()


class SavedLessonServiceTests(unittest.TestCase):
    def test_list_returns_only_published_saved_topics(self):
        from datetime import datetime, timezone
        fake = Connection([Cursor(rows=[{
            "id":"topic-1","title":"Atomic Structure","summary":"Atoms and particles",
            "class_level":"SS1","subject":"Chemistry",
            "created_at":datetime(2026,11,7,tzinfo=timezone.utc)
        }])])
        with patch.object(saved, "connection", return_value=fake):
            result = saved.list_saved_lessons("student-1")
        self.assertEqual(result["items"][0]["topic_id"], "topic-1")
        self.assertIn("t.status='published'", fake.calls[0][0])
        self.assertIn("t.curriculum_status='published'", fake.calls[0][0])

    def test_save_is_idempotent(self):
        fake = Connection([Cursor({"id":"topic-1"}), Cursor({"topic_id":"topic-1"})])
        with patch.object(saved, "connection", return_value=fake):
            result = saved.save_lesson("student-1", "topic-1")
        self.assertTrue(result["saved"])
        self.assertFalse(result["already_saved"])
        self.assertIn("ON CONFLICT (student_id,topic_id) DO NOTHING", fake.calls[1][0])

    def test_duplicate_save_does_not_create_duplicate(self):
        fake = Connection([Cursor({"id":"topic-1"}), Cursor(None)])
        with patch.object(saved, "connection", return_value=fake):
            result = saved.save_lesson("student-1", "topic-1")
        self.assertTrue(result["already_saved"])

    def test_unpublished_topic_cannot_be_saved(self):
        fake = Connection([Cursor(None)])
        with patch.object(saved, "connection", return_value=fake):
            with self.assertRaises(SavedLessonError) as caught:
                saved.save_lesson("student-1", "topic-1")
        self.assertEqual(caught.exception.status, 404)

    def test_remove_reports_whether_a_bookmark_existed(self):
        fake = Connection([Cursor({"topic_id":"topic-1"})])
        with patch.object(saved, "connection", return_value=fake):
            result = saved.remove_saved_lesson("student-1", "topic-1")
        self.assertFalse(result["saved"])
        self.assertTrue(result["removed"])


class SavedLessonRouteSecurityTests(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_list_requires_student_session(self):
        with patch("app._current_student", return_value=None):
            response = self.client.get("/api/v1/student/saved-lessons")
        self.assertEqual(response.status_code, 401)

    def test_save_requires_student_session_and_csrf(self):
        with patch("app._current_student", return_value=None):
            response = self.client.post(
                "/api/v1/student/saved-lessons/00000000-0000-0000-0000-000000000001"
            )
        self.assertEqual(response.status_code, 401)

    def test_remove_requires_student_session_and_csrf(self):
        with patch("app._current_student", return_value=None):
            response = self.client.delete(
                "/api/v1/student/saved-lessons/00000000-0000-0000-0000-000000000001"
            )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
