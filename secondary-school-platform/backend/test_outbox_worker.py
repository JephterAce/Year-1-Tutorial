import os
import sys
import types
import unittest
from unittest import mock

import outbox_worker


class OutboxWorkerTests(unittest.TestCase):
    def setUp(self):
        outbox_worker._thread = None

    def test_disabled_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(outbox_worker.start_outbox_worker())

    def test_starts_once_when_enabled(self):
        fake = mock.Mock()
        with mock.patch.dict(os.environ, {"PAYMENT_OUTBOX_WORKER_ENABLED": "true"}, clear=True), \
                mock.patch.object(outbox_worker.threading, "Thread", return_value=fake):
            self.assertTrue(outbox_worker.start_outbox_worker())
            self.assertFalse(outbox_worker.start_outbox_worker())
        fake.start.assert_called_once()

    def test_idle_without_smtp(self):
        env = {"DATABASE_URL": "postgresql://x"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(outbox_worker.run_once(), "smtp_not_configured")

    def test_idle_without_database(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(outbox_worker.run_once(), "no_database")

    def test_processes_when_configured(self):
        env = {"DATABASE_URL": "postgresql://x", "SMTP_HOST": "h", "SMTP_USERNAME": "u", "SMTP_PASSWORD": "p"}
        fake_module = types.SimpleNamespace(process_one_outbox_item=lambda: {"status": "sent"})
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.dict(sys.modules, {"payment_outbox": fake_module}):
            self.assertEqual(outbox_worker.run_once(), "sent")


if __name__ == "__main__":
    unittest.main()
