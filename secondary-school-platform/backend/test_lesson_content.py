import unittest
from unittest.mock import patch

import lesson_content
from lesson_content import (
    LessonContentError, check_practice_answer, get_lesson_content, mark_topic_complete
)
from podcast_production import build_podcast_script, PodcastProductionError


class FakeCursor:
    def __init__(self, row=None, rows=None):
        self.row, self.rows = row, rows or []
    def fetchone(self):
        return self.row
    def fetchall(self):
        return self.rows


class FakeConnection:
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
        return FakeCursor()


class LessonContentServiceTests(unittest.TestCase):
    def test_content_response_contains_no_answer_keys(self):
        fake = FakeConnection([
            FakeCursor({"entitled": 1}),
            FakeCursor({
                "id": "content-1", "version": 2,
                "content_json": {"intro": "Cells are basic units of life."}
            }),
            FakeCursor(rows=[{
                "id": "question-1", "question_type": "single_choice",
                "prompt": "Which organelle releases energy?",
                "options": [{"id": "a", "text": "Mitochondrion"}],
                "points": 1, "sort_order": 1
            }])
        ])
        with patch.object(lesson_content, "connection", return_value=fake):
            result = get_lesson_content("student-1", "topic-1")
        self.assertEqual(result["version"], 2)
        self.assertNotIn("answer_key", str(result))
        self.assertEqual(result["practice"][0]["id"], "question-1")

    def test_locked_lesson_rejects_content_access(self):
        fake = FakeConnection([FakeCursor(None)])
        with patch.object(lesson_content, "connection", return_value=fake):
            with self.assertRaises(LessonContentError) as caught:
                get_lesson_content("student-1", "topic-1")
        self.assertEqual(caught.exception.status, 402)

    def test_practice_answer_returns_feedback_not_answer_key(self):
        fake = FakeConnection([
            FakeCursor({"entitled": 1}),
            FakeCursor({
                "question_type": "single_choice",
                "answer_key": {"value": "b"},
                "explanation": "The mitochondrion is the main site of aerobic respiration."
            })
        ])
        with patch.object(lesson_content, "connection", return_value=fake):
            result = check_practice_answer("student-1", "topic-1", "q-1", "B")
        self.assertTrue(result["correct"])
        self.assertNotIn("answer_key", result)

    def test_mark_complete_requires_entitlement_and_approved_content(self):
        fake = FakeConnection([
            FakeCursor({"entitled": 1}),
            FakeCursor({"id": "content-1"}),
            FakeCursor()
        ])
        with patch.object(lesson_content, "connection", return_value=fake):
            result = mark_topic_complete("student-1", "topic-1")
        self.assertTrue(result["completed"])
        self.assertTrue(any("INSERT INTO student_topic_progress" in sql for sql, _ in fake.calls))


class PodcastScriptTests(unittest.TestCase):
    def test_script_is_two_presenter_and_bounded_to_approved_content(self):
        script = build_podcast_script("Cell Structure", "Biology", {
            "intro": "Cells are the basic structural units of living organisms.",
            "learning_objectives": ["Identify major cell structures."],
            "sections": [{"heading": "The nucleus", "body": "The nucleus contains genetic material."}],
            "key_terms": [{"term": "Cytoplasm", "definition": "The material inside the cell membrane."}],
            "worked_examples": [{"title": "Cell comparison", "problem": "Compare two cell types.",
                                 "steps": ["Identify shared structures."], "answer": "Use the stated features."}]
        })
        self.assertIn("HOST 1:", script)
        self.assertIn("HOST 2:", script)
        self.assertIn("The nucleus contains genetic material.", script)
        self.assertIn("Identify shared structures.", script)

    def test_script_requires_structured_approved_lesson_content(self):
        with self.assertRaises(PodcastProductionError):
            build_podcast_script("Cell Structure", "Biology", None)


class StudentLearningRouteSecurityTests(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_dashboard_requires_student_session(self):
        with patch("app._current_student", return_value=None):
            response = self.client.get("/api/v1/student/dashboard")
        self.assertEqual(response.status_code, 401)

    def test_lesson_notes_require_student_session(self):
        with patch("app._current_student", return_value=None):
            response = self.client.get("/api/v1/topics/topic-1/lesson-content")
        self.assertEqual(response.status_code, 401)


    def test_admin_lesson_authoring_requires_admin_session(self):
        response = self.client.post(
            "/api/v1/admin/topics/00000000-0000-0000-0000-000000000001/lesson-content",
            json={"content": {}, "practice_questions": []}
        )
        self.assertEqual(response.status_code, 401)

    def test_admin_lesson_review_requires_admin_session(self):
        response = self.client.post(
            "/api/v1/admin/lesson-content/00000000-0000-0000-0000-000000000001/review",
            json={"review_status": "approved", "teacher_reviewer_name": "Qualified reviewer"}
        )
        self.assertEqual(response.status_code, 401)


    def test_curriculum_source_capture_requires_admin_session(self):
        response = self.client.post(
            "/api/v1/admin/curriculum-sources",
            json={"class_level":"SS1","subject_slug":"biology",
                  "source_title":"NERDC Biology SSS1","source_url":"https://example.invalid/source",
                  "source_section":"Page 1"}
        )
        self.assertEqual(response.status_code, 401)

    def test_curriculum_topic_publication_requires_admin_session(self):
        response = self.client.post(
            "/api/v1/admin/topics/00000000-0000-0000-0000-000000000001/publish",
            json={"teacher_reviewer_name":"Qualified teacher",
                  "curriculum_evidence_note":"Evidence checked."}
        )
        self.assertEqual(response.status_code, 401)

    def test_practice_submission_requires_session_and_csrf(self):
        with patch("app._current_student", return_value=None) as current:
            response = self.client.post(
                "/api/v1/topics/topic-1/practice/question-1",
                json={"answer": "A"}
            )
        self.assertEqual(response.status_code, 401)
        current.assert_called_once_with(require_csrf=True)


if __name__ == "__main__":
    unittest.main()
