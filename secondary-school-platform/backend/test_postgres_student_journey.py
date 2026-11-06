"""Disposable-PostgreSQL registration-to-results student journey acceptance test."""
import os
import unittest
from uuid import uuid4
from unittest.mock import patch

import psycopg
from psycopg.types.json import Jsonb

from database import connection


class StudentRegistrationToResultsJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dsn = os.environ.get("DATABASE_URL")
        if not cls.dsn:
            raise unittest.SkipTest("Disposable DATABASE_URL required.")

    def setUp(self):
        self.client = None
        self.student_id = None
        self.topic_id = str(uuid4())
        self.source_id = str(uuid4())
        self.assessment_id = str(uuid4())
        self.email = f"journey-{uuid4().hex[:12]}@integration.invalid"
        self.username = f"journey_{uuid4().hex[:10]}"
        self.password = "Integration-Learner-2026!"
        self.env = patch.dict(os.environ, {
            "APP_ENV": "test",
            "STUDENT_REGISTRATION_ENABLED": "true",
            "AUTH_RATE_LIMIT_PEPPER": "integration-test-pepper-" + ("x" * 48),
            "PRIVACY_NOTICE_VERSION": "ci-test-1",
            "TERMS_VERSION": "ci-test-1",
        })
        self.env.start()

    def tearDown(self):
        with connection() as conn:
            if not self.student_id:
                row=conn.execute("SELECT id FROM students WHERE email=%s",(self.email,)).fetchone()
                self.student_id=str(row["id"]) if row else None
            if self.student_id:
                conn.execute("DELETE FROM students WHERE id=%s", (self.student_id,))
            conn.execute("DELETE FROM assessments WHERE id=%s", (self.assessment_id,))
            conn.execute("DELETE FROM topics WHERE id=%s", (self.topic_id,))
            conn.execute("DELETE FROM curriculum_source_records WHERE id=%s", (self.source_id,))
        self.env.stop()

    def test_registration_to_lesson_practice_progress_and_results(self):
        from app import app
        self.client = app.test_client()
        captured = {}

        def capture_identity_link(email, token, purpose):
            captured.update(email=email, token=token, purpose=purpose)

        with patch("identity_email.send_identity_link", side_effect=capture_identity_link):
            response = self.client.post("/api/v1/auth/register", json={
                "email": self.email,
                "username": self.username,
                "display_name": "Integration Learner",
                "class_level": "SS1",
                "password": self.password,
                "accept_terms": True,
                "accept_privacy": True,
            })
        self.assertEqual(response.status_code, 202)
        self.assertEqual(captured["purpose"], "verify")
        self.assertEqual(captured["email"], self.email)

        verified = self.client.post("/api/v1/auth/verify-email", json={"token": captured["token"]})
        self.assertEqual(verified.status_code, 200)
        self.assertTrue(verified.get_json()["verified"])

        logged_in = self.client.post("/api/v1/auth/login", json={
            "email": self.email, "password": self.password
        })
        self.assertEqual(logged_in.status_code, 200)
        self.assertTrue(logged_in.get_json()["authenticated"])
        csrf = self.client.get_cookie("learnwise_csrf").value
        headers = {"X-CSRF-Token": csrf}

        identity = self.client.get("/api/v1/auth/me")
        self.assertEqual(identity.status_code, 200)
        self.student_id = identity.get_json()["student"]["id"]
        self.assertEqual(identity.get_json()["student"]["class_level"], "SS1")

        with connection() as conn:
            subject = conn.execute(
                "SELECT id FROM subjects WHERE slug='general-mathematics'"
            ).fetchone()
            version = conn.execute(
                "SELECT id FROM curriculum_versions WHERE version_code='nerdc_ssec_2025'"
            ).fetchone()
            conn.execute(
                """INSERT INTO curriculum_source_records
                   (id,subject_id,class_level,source_title,source_url,source_section,
                    verification_status,curriculum_version_id,source_kind,licence_status,
                    reviewed_by,reviewed_at)
                   VALUES (%s,%s,'SS1','Synthetic CI source','https://example.invalid/ci',
                    'Synthetic section','approved',%s,'official_nerdc','permission_granted',
                    'CI reviewer',now())""",
                (self.source_id, subject["id"], version["id"]),
            )
            conn.execute(
                """INSERT INTO topics
                   (id,subject_id,class_level,term_id,slug,title,summary,learning_objectives,
                    price_kobo,currency,status,curriculum_version_id,curriculum_source_record_id,
                    curriculum_status,curriculum_evidence_note,curriculum_approved_by,
                    curriculum_approved_at,term_mapping_status)
                   VALUES (%s,%s,'SS1',NULL,'ci-student-journey','Synthetic Algebra Lesson',
                    'A test-only lesson.',%s,100000,'NGN','published',%s,%s,'published',
                    'Synthetic integration evidence','CI reviewer',now(),'not_assigned')""",
                (self.topic_id, subject["id"], Jsonb(["Solve a simple linear equation."]),
                 version["id"], self.source_id),
            )
            content_id = str(uuid4())
            conn.execute(
                """INSERT INTO topic_lesson_content
                   (id,topic_id,version,content_json,review_status,approved_by,approved_at)
                   VALUES (%s,%s,1,%s,'approved','CI reviewer',now())""",
                (content_id,self.topic_id,Jsonb({
                    "intro":"An equation states that two expressions have equal value.",
                    "learning_objectives":["Solve a simple linear equation."],
                    "sections":[{"heading":"Balance method","body":"Do the same operation to both sides."}],
                    "key_terms":[{"term":"Variable","definition":"A symbol representing an unknown value."}],
                    "worked_examples":[{"title":"Solve x + 3 = 7","problem":"Find x.",
                                        "steps":["Subtract 3 from both sides."],"answer":"x = 4"}]
                })),
            )
            practice_id = str(uuid4())
            conn.execute(
                """INSERT INTO lesson_practice_questions
                   (id,topic_id,lesson_content_id,question_type,prompt,options,answer_key,
                    explanation,review_status)
                   VALUES (%s,%s,%s,'single_choice','What is x if x + 3 = 7?',
                    %s,%s,'Subtract 3 from both sides, so x = 4.','approved')""",
                (practice_id,self.topic_id,content_id,
                 Jsonb([{"id":"a","text":"3"},{"id":"b","text":"4"}]),
                 Jsonb({"value":"b"})),
            )
            conn.execute(
                "INSERT INTO entitlements(student_id,topic_id,grant_reason) VALUES (%s,%s,'integration_test')",
                (self.student_id,self.topic_id),
            )
            conn.execute(
                """INSERT INTO assessments
                   (id,subject_id,class_level,title,status,version,allowed_question_counts,
                    max_attempts,pass_mark_percent)
                   VALUES (%s,%s,'SS1','CI Student Journey Test','published',1,ARRAY[1],1,50)""",
                (self.assessment_id,subject["id"]),
            )
            question_id = str(uuid4())
            conn.execute(
                """INSERT INTO assessment_questions
                   (id,assessment_id,question_type,prompt,options,answer_key,points,sort_order,is_active)
                   VALUES (%s,%s,'single_choice',%s,%s,%s,2,1,true)""",
                (question_id,self.assessment_id,Jsonb({"text":"2 + 2 = ?"}),
                 Jsonb([{"id":"a","text":"4"},{"id":"b","text":"5"}]),
                 Jsonb({"correct_option_id":"a"})),
            )

        notes = self.client.get(f"/api/v1/topics/{self.topic_id}/lesson-content")
        self.assertEqual(notes.status_code, 200)
        self.assertIn("Balance method", str(notes.get_json()["content"]))
        self.assertNotIn("answer_key", str(notes.get_json()))

        practice = self.client.post(
            f"/api/v1/topics/{self.topic_id}/practice/{practice_id}",
            json={"answer":"b"}, headers=headers
        )
        self.assertEqual(practice.status_code, 200)
        self.assertTrue(practice.get_json()["correct"])

        completed = self.client.post(
            f"/api/v1/topics/{self.topic_id}/progress/complete",
            json={}, headers=headers
        )
        self.assertEqual(completed.status_code, 200)

        dashboard = self.client.get("/api/v1/student/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.get_json()["summary"]["completed_lessons"], 1)

        created = self.client.post(
            f"/api/v1/assessments/{self.assessment_id}/attempts",
            json={"question_count":1}, headers=headers
        )
        self.assertEqual(created.status_code, 201)
        attempt = created.get_json()["attempt_id"]
        started = self.client.post(
            f"/api/v1/assessment-attempts/{attempt}/start",
            json={"accepted":True,"policy_version":created.get_json()["policy_version"]},
            headers=headers
        )
        self.assertEqual(started.status_code, 200)
        self.assertNotIn("answer_key", str(started.get_json()))

        saved = self.client.put(
            f"/api/v1/assessment-attempts/{attempt}/answers/{question_id}",
            json={"answer":"a"}, headers=headers
        )
        self.assertEqual(saved.status_code, 200)
        submitted = self.client.post(
            f"/api/v1/assessment-attempts/{attempt}/submit",
            json={}, headers=headers
        )
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.get_json()["percentage"], "100.00")

        history = self.client.get("/api/v1/student/assessment-history")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.get_json()["items"]), 1)
        self.assertEqual(history.get_json()["items"][0]["percentage"], "100.00")


if __name__ == "__main__":
    unittest.main()
