import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class AdminSecurityMigrationTests(unittest.TestCase):
    def test_admin_sessions_store_only_hashes_and_expiry_state(self):
        sql = (ROOT / "migrations" / "013_admin_sessions_and_audit_guard.sql").read_text()
        self.assertIn("CREATE TABLE IF NOT EXISTS admin_sessions", sql)
        self.assertIn("session_id_hash CHAR(64) NOT NULL UNIQUE", sql)
        self.assertIn("csrf_token_hash CHAR(64) NOT NULL", sql)
        self.assertIn("expires_at TIMESTAMPTZ NOT NULL", sql)
        self.assertIn("revoked_at TIMESTAMPTZ", sql)
        self.assertNotIn("session_token TEXT", sql)

    def test_audit_events_are_append_only(self):
        sql = (ROOT / "migrations" / "013_admin_sessions_and_audit_guard.sql").read_text()
        self.assertIn("BEFORE UPDATE OR DELETE ON audit_events", sql)
        self.assertIn("learnwise_reject_audit_mutation", sql)

    def test_admin_email_lookup_is_case_and_space_insensitive(self):
        sql = (ROOT / "migrations" / "013_admin_sessions_and_audit_guard.sql").read_text()
        self.assertIn("lower(trim(email))", sql)

    def test_admin_auth_is_not_implicitly_enabled(self):
        sql = (ROOT / "migrations" / "013_admin_sessions_and_audit_guard.sql").read_text()
        self.assertIn("No admin login route is enabled", sql)


if __name__ == "__main__":
    unittest.main()
