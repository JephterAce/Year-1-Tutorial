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

    def test_admin_smtp_diagnostic_uses_separate_one_per_hour_rate_limit(self):
        from unittest.mock import MagicMock
        connection = MagicMock()
        connection.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = {
            "attempts": 1, "blocked_until": None
        }
        with patch.dict("os.environ", {"AUTH_RATE_LIMIT_PEPPER": "p" * 40}), patch.object(
            admin_auth, "connection", connection
        ):
            admin_auth.reserve_admin_smtp_diagnostic("Owner@Example.test")
        sql, params = connection.return_value.__enter__.return_value.execute.call_args.args
        self.assertEqual(sql.count("%s"), len(params))
        self.assertEqual(params[0], "admin_smtp_diagnostic")
        self.assertEqual(params[2:5], (60, 60, 60))
        self.assertEqual(params[5:], (1, 60))

    def test_admin_smtp_diagnostic_rate_limit_fails_closed(self):
        from unittest.mock import MagicMock
        connection = MagicMock()
        connection.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = {
            "attempts": 2, "blocked_until": None
        }
        with patch.dict("os.environ", {"AUTH_RATE_LIMIT_PEPPER": "p" * 40}), patch.object(
            admin_auth, "connection", connection
        ):
            with self.assertRaises(admin_auth.AdminAuthError):
                admin_auth.reserve_admin_smtp_diagnostic("owner@example.test")

if __name__ == "__main__":
    unittest.main()
