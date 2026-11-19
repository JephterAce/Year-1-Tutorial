"""Opt-in database-backed assessment and Paystack sandbox-flow integration tests.

CI runs these only against its disposable PostgreSQL database. Provider HTTP is
stubbed with Paystack-shaped responses; no live payment or secret is used.
"""
import hashlib
import hmac
import json
import os
import unittest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

import psycopg
from psycopg.types.json import Jsonb

from database import connection
from assessment_attempts import create_attempt, start_attempt, save_answer, submit_attempt
from payment_orders import create_topic_checkout
from payments import process_paystack_charge_success
from paystack_verification import verify_paystack_transaction


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class PostgreSQLEndToEndFlows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dsn = os.environ.get("DATABASE_URL")
        if not cls.dsn:
            raise unittest.SkipTest("Disposable DATABASE_URL required.")

    def setUp(self):
        self.student = str(uuid4())
        self.subject = str(uuid4())
        self.assessment = None
        self.topic = None
        self.source = None
        with connection() as conn:
            conn.execute(
                """INSERT INTO students(id,email,display_name,class_level,account_status,email_verified_at)
                   VALUES (%s,%s,'Integration learner','SS1','active',now())""",
                (self.student, self.student + "@integration.invalid"),
            )
            subject = conn.execute(
                "SELECT id FROM subjects WHERE slug='general-mathematics'"
            ).fetchone()
            self.subject = str(subject["id"])

    def tearDown(self):
        with connection() as conn:
            if self.topic:
                conn.execute("DELETE FROM payment_notification_outbox WHERE payment_id IN (SELECT id FROM payment_transactions WHERE topic_id=%s)", (self.topic,))
                conn.execute("DELETE FROM entitlements WHERE topic_id=%s", (self.topic,))
                conn.execute("DELETE FROM payment_webhook_events WHERE payload->>'reference' IN (SELECT provider_reference FROM payment_transactions WHERE topic_id=%s)", (self.topic,))
                conn.execute("DELETE FROM payment_transactions WHERE topic_id=%s", (self.topic,))
                conn.execute("DELETE FROM topics WHERE id=%s", (self.topic,))
            if self.source:
                conn.execute("DELETE FROM curriculum_source_records WHERE id=%s", (self.source,))
            conn.execute("DELETE FROM students WHERE id=%s", (self.student,))

    def test_assessment_attempt_start_save_and_grade(self):
        self.assessment = str(uuid4())
        question = str(uuid4())
        with connection() as conn:
            conn.execute(
                """INSERT INTO assessments(id,subject_id,class_level,title,status,version,
                   allowed_question_counts,max_attempts,pass_mark_percent)
                   VALUES (%s,%s,'SS1','CI Algebra Test','published',1,ARRAY[1],1,50)""",
                (self.assessment, self.subject),
            )
            conn.execute(
                """INSERT INTO assessment_questions(id,assessment_id,question_type,prompt,options,
                   answer_key,points,sort_order,is_active)
                   VALUES (%s,%s,'single_choice',%s,%s,%s,2,1,true)""",
                (question, self.assessment, Jsonb({"text":"2 + 2 = ?"}),
                 Jsonb([{"id":"a","text":"4"},{"id":"b","text":"5"}]),
                 Jsonb({"correct_option_id":"a"})),
            )
        created = create_attempt(self.student, self.assessment, 1)
        started = start_attempt(self.student, created["attempt_id"], True, created["policy_version"])
        self.assertEqual(started["status"], "in_progress")
        self.assertNotIn("answer_key", started["questions"][0])
        save_answer(self.student, created["attempt_id"], question, "a")
        result = submit_attempt(self.student, created["attempt_id"])
        self.assertEqual(result["status"], "submitted")
        self.assertEqual(Decimal(result["score"]), Decimal("2"))
        self.assertEqual(result["percentage"], "100.00")

    def test_paystack_checkout_webhook_verify_and_entitlement_are_idempotent(self):
        self.topic = str(uuid4())
        self.source = str(uuid4())
        with connection() as conn:
            version = conn.execute(
                "SELECT id FROM curriculum_versions WHERE version_code='nerdc_ssec_2025'"
            ).fetchone()["id"]
            conn.execute(
                """INSERT INTO curriculum_source_records
                   (id,subject_id,class_level,source_title,source_url,source_section,
                    verification_status,curriculum_version_id,source_kind,licence_status,
                    reviewed_by,reviewed_at)
                   VALUES (%s,%s,'SS1','Synthetic CI source','https://example.invalid/ci',
                    'Test section','approved',%s,'official_nerdc','permission_granted',
                    'CI reviewer',now())""",
                (self.source, self.subject, version),
            )
            conn.execute(
                """INSERT INTO topics
                   (id,subject_id,class_level,term_id,slug,title,price_kobo,currency,status,
                    curriculum_version_id,curriculum_source_record_id,curriculum_status,
                    curriculum_evidence_note,curriculum_approved_by,curriculum_approved_at,
                    term_mapping_status)
                   VALUES (%s,%s,'SS1',NULL,'ci-topic','CI test lesson',100000,'NGN',
                    'published',%s,%s,'published','Synthetic integration evidence',
                    'CI reviewer',now(),'not_assigned')""",
                (self.topic, self.subject, version, self.source),
            )

        secret = "ci-paystack-secret-not-live"
        def checkout_opener(request, timeout=0):
            payload = json.loads(request.data.decode())
            return FakeResponse({"status":True,"data":{
                "reference":payload["reference"],
                "authorization_url":"https://checkout.paystack.com/ci-test",
                "access_code":"ci-access-code"
            }})
        with patch.dict("os.environ", {"PAYSTACK_SECRET_KEY":secret,
                                       "PUBLIC_APP_URL":"https://learnwise.invalid"}):
            checkout = create_topic_checkout(self.student, self.topic, opener=checkout_opener)
            event = {"event":"charge.success","data":{
                "reference":checkout["reference"],"amount":checkout["amount_kobo"],
                "currency":"NGN","status":"success"
            }}
            raw = json.dumps(event,separators=(",",":")).encode()
            signature = hmac.new(secret.encode(),raw,hashlib.sha512).hexdigest()

            def verification_opener(request, timeout=0):
                return FakeResponse({"status":True,"data":{
                    "reference":checkout["reference"],"amount":checkout["amount_kobo"],
                    "currency":"NGN","status":"success","paid_at":"2026-11-02T00:00:00Z"
                }})
            with patch("payments.verify_paystack_transaction",
                       side_effect=lambda reference, amount, secret=None:
                           verify_paystack_transaction(reference, amount, secret=secret,
                                                        opener=verification_opener)):
                first = process_paystack_charge_success(raw,signature)
                second = process_paystack_charge_success(raw,signature)

        self.assertEqual(first["status"],"successful")
        self.assertEqual(second["status"],"successful")
        with connection() as conn:
            entitlement = conn.execute(
                "SELECT count(*) AS n FROM entitlements WHERE student_id=%s AND topic_id=%s AND revoked_at IS NULL",
                (self.student,self.topic),
            ).fetchone()["n"]
            outbox = conn.execute(
                "SELECT count(*) AS n FROM payment_notification_outbox WHERE dedupe_key LIKE %s",
                ("paystack:owner-alert:%",),
            ).fetchone()["n"]
        self.assertEqual(entitlement,1)
        self.assertGreaterEqual(outbox,1)


if __name__ == "__main__":
    unittest.main()
