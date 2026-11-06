import unittest
from unittest.mock import patch

import admin_auth


class AdminAuthPrimitiveTests(unittest.TestCase):
    def test_csrf_rejects_missing_and_wrong_tokens(self):
        self.assertFalse(admin_auth.validate_admin_csrf(None, "x"))
        self.assertFalse(admin_auth.validate_admin_csrf({"csrf_token_hash": "0" * 64}, "x"))

    def test_csrf_accepts_matching_token_digest(self):
        token = "test-csrf-token"
        session = {"csrf_token_hash": admin_auth._digest(token)}
        self.assertTrue(admin_auth.validate_admin_csrf(session, token))

    def test_logout_ignores_missing_session(self):
        with patch.object(admin_auth, "connection") as conn:
            admin_auth.logout_admin(None)
            conn.assert_not_called()

    def test_audit_metadata_validation(self):
        with self.assertRaises(ValueError):
            admin_auth.record_admin_audit("admin", "", "topic", "1")
        with self.assertRaises(ValueError):
            admin_auth.record_admin_audit("admin", "edit", "topic", "1", [])

if __name__ == "__main__":
    unittest.main()
