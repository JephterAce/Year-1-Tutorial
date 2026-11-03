import unittest
import os
from unittest import mock
from assessment_attempts import check_answer_size, AttemptError, entitlement_required
from app import app


class AttemptHardeningTests(unittest.TestCase):
    def test_normal_answers_pass(self):
        for a in ("42", ["a", "b"], True, None):
            check_answer_size(a)

    def test_oversized_answers_rejected(self):
        for a in ("x" * 501, ["a"] * 21, ["y" * 101]):
            with self.assertRaises(AttemptError):
                check_answer_size(a)

    def test_entitlement_flag_defaults_off(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(entitlement_required())
        with mock.patch.dict(os.environ, {"ASSESSMENT_REQUIRES_ENTITLEMENT": "1"}):
            self.assertTrue(entitlement_required())

    def test_security_headers_present(self):
        r = app.test_client().get("/health")
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")
        self.assertEqual(r.headers["Referrer-Policy"], "same-origin")


if __name__ == "__main__":
    unittest.main()
