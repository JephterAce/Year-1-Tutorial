import os
import unittest
from unittest.mock import MagicMock, patch

import bootstrap_admin


class BootstrapAdminTests(unittest.TestCase):
    def _connection(self, admin_count):
        conn = MagicMock()
        count_result = MagicMock()
        count_result.fetchone.return_value = {"admin_count": admin_count}
        conn.execute.side_effect = [MagicMock(), count_result]
        manager = MagicMock()
        manager.__enter__.return_value = conn
        manager.__exit__.return_value = False
        return conn, manager

    def test_requires_explicit_confirmation_before_database_access(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(bootstrap_admin, "connection") as db:
            with self.assertRaises(SystemExit):
                bootstrap_admin.main()
            db.assert_not_called()

    def test_requires_database_url(self):
        env = {
            "LEARNWISE_BOOTSTRAP_CONFIRM": "CREATE_OWNER_ADMIN",
            "LEARNWISE_ADMIN_EMAIL": "owner@example.com",
            "LEARNWISE_ADMIN_PASSWORD": "a-very-long-strong-password",
        }
        with patch.dict(os.environ, env, clear=True), patch.object(bootstrap_admin, "connection") as db:
            with self.assertRaises(SystemExit):
                bootstrap_admin.main()
            db.assert_not_called()

    def test_refuses_any_existing_admin_not_only_same_email(self):
        env = {
            "DATABASE_URL": "postgresql://placeholder",
            "LEARNWISE_BOOTSTRAP_CONFIRM": "CREATE_OWNER_ADMIN",
            "LEARNWISE_ADMIN_EMAIL": "second-owner@example.com",
            "LEARNWISE_ADMIN_PASSWORD": "a-very-long-strong-password",
        }
        conn, manager = self._connection(admin_count=1)
        with patch.dict(os.environ, env, clear=True), patch.object(
            bootstrap_admin, "connection", return_value=manager
        ), patch.object(bootstrap_admin, "hash_password", return_value="hashed"):
            with self.assertRaises(SystemExit):
                bootstrap_admin.main()
        self.assertEqual(conn.execute.call_count, 2)
        self.assertIn("pg_advisory_xact_lock", conn.execute.call_args_list[0].args[0])
        self.assertNotIn("INSERT INTO admin_users", str(conn.execute.call_args_list))

    def test_normalises_email_before_insert_path(self):
        self.assertEqual(bootstrap_admin.normalise_email(" Owner@Example.com "), "owner@example.com")


if __name__ == "__main__":
    unittest.main()
