"""Disposable-PostgreSQL lifecycle tests for short-lived synthetic QA identities."""
import hashlib
import os
import unittest
from uuid import uuid4
from unittest.mock import patch

from database import connection
from identity_service import (
    provision_synthetic_qa_student, verify_student_email, login_student,
    authenticate_session, revoke_synthetic_qa_student, expire_synthetic_qa_students,
    IdentityError,
)


class PostgreSQLSyntheticQAIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get("DATABASE_URL"):
            raise unittest.SkipTest("Disposable DATABASE_URL required.")

    def setUp(self):
        self.email = f"synthetic-qa-{uuid4().hex[:12]}@integration.invalid"
        self.student_id = None
        self.env = patch.dict(os.environ, {
            "APP_ENV": "staging",
            "STAGING_QA_IDENTITY_ENABLED": "true",
            "STAGING_QA_EMAIL": self.email,
            "STUDENT_REGISTRATION_ENABLED": "false",
            "AUTH_RATE_LIMIT_PEPPER": "synthetic-qa-integration-pepper-" + ("x" * 40),
        })
        self.env.start()

    def tearDown(self):
        if self.student_id:
            with connection() as conn:
                conn.execute("DELETE FROM students WHERE id=%s AND is_synthetic_qa=true", (self.student_id,))
        self.env.stop()

    def create_identity(self):
        result = provision_synthetic_qa_student()
        self.student_id = str(result["student"]["id"])
        return result

    def test_provision_verify_login_and_no_consent_records(self):
        result = self.create_identity()
        token_digest = hashlib.sha256(result["verification_token"].encode()).hexdigest()
        with connection() as conn:
            token = conn.execute(
                """SELECT purpose,token_hash FROM identity_tokens
                   WHERE student_id=%s""", (self.student_id,)
            ).fetchone()
            consents = conn.execute(
                "SELECT count(*) AS n FROM student_consent_records WHERE student_id=%s",
                (self.student_id,),
            ).fetchone()["n"]
            student = conn.execute(
                """SELECT is_synthetic_qa,account_status,synthetic_qa_expires_at
                   FROM students WHERE id=%s""", (self.student_id,)
            ).fetchone()
        self.assertEqual(token["purpose"], "verify_qa_email")
        self.assertEqual(token["token_hash"], token_digest)
        self.assertEqual(consents, 0)
        self.assertTrue(student["is_synthetic_qa"])
        self.assertEqual(student["account_status"], "pending")
        self.assertIsNotNone(student["synthetic_qa_expires_at"])

        self.assertTrue(verify_student_email(result["verification_token"]))
        session = login_student(self.email, result["temporary_password"])
        authenticated = authenticate_session(session["session_id"])
        self.assertTrue(authenticated["is_synthetic_qa"])
        self.assertEqual(str(authenticated["student_id"]), self.student_id)

    def test_expiry_blocks_login_and_session_then_closes_identity(self):
        result = self.create_identity()
        verify_student_email(result["verification_token"])
        session = login_student(self.email, result["temporary_password"])
        with connection() as conn:
            conn.execute(
                "UPDATE students SET synthetic_qa_expires_at=now()-interval '1 second' WHERE id=%s",
                (self.student_id,),
            )
        with self.assertRaises(IdentityError):
            login_student(self.email, result["temporary_password"])
        self.assertIsNone(authenticate_session(session["session_id"]))
        self.assertEqual(expire_synthetic_qa_students(), 1)
        with connection() as conn:
            row = conn.execute(
                """SELECT account_status,email FROM students WHERE id=%s""",
                (self.student_id,),
            ).fetchone()
            sessions = conn.execute(
                "SELECT count(*) AS n FROM student_sessions WHERE student_id=%s AND revoked_at IS NULL",
                (self.student_id,),
            ).fetchone()["n"]
        self.assertEqual(row["account_status"], "closed")
        self.assertIsNone(row["email"])
        self.assertEqual(sessions, 0)

    def test_owner_revocation_invalidates_sessions_and_clears_mailbox(self):
        result = self.create_identity()
        verify_student_email(result["verification_token"])
        session = login_student(self.email, result["temporary_password"])
        self.assertTrue(revoke_synthetic_qa_student(self.student_id))
        self.assertIsNone(authenticate_session(session["session_id"]))
        with connection() as conn:
            row = conn.execute(
                "SELECT account_status,email FROM students WHERE id=%s",
                (self.student_id,),
            ).fetchone()
            tokens = conn.execute(
                "SELECT count(*) AS n FROM identity_tokens WHERE student_id=%s AND consumed_at IS NULL",
                (self.student_id,),
            ).fetchone()["n"]
        self.assertEqual(row["account_status"], "closed")
        self.assertIsNone(row["email"])
        self.assertEqual(tokens, 0)

    def test_provisioning_fails_closed_without_staging_feature_flag(self):
        with patch.dict(os.environ, {"STAGING_QA_IDENTITY_ENABLED": "false"}):
            with self.assertRaises(IdentityError):
                provision_synthetic_qa_student()


if __name__ == "__main__":
    unittest.main()
