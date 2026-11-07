"""PostgreSQL integration checks; run only after disposable migrations."""
import os
import unittest

import psycopg

from database import database_ready, list_published_topics
from rehearse_migrations import rehearse


class PostgreSQLSchemaIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dsn = os.environ.get("DATABASE_URL")
        if not cls.dsn:
            raise unittest.SkipTest("DATABASE_URL is required for PostgreSQL integration tests.")

    def test_database_is_ready_and_published_catalogue_query_runs(self):
        self.assertTrue(database_ready())
        self.assertEqual(list_published_topics(), [])

    def test_baseline_and_all_numbered_migrations_recorded(self):
        with psycopg.connect(self.dsn) as conn:
            rows = conn.execute(
                "SELECT version FROM learnwise_schema_migrations ORDER BY version"
            ).fetchall()
            self.assertEqual(len(rows), 19)
            self.assertEqual(rows[0][0], "000_DATABASE_SCHEMA.sql")
            self.assertEqual(rows[-1][0], "018_student_saved_topics.sql")


    def test_ai_quota_and_lesson_content_tables_exist(self):
        with psycopg.connect(self.dsn) as conn:
            names = conn.execute(
                """SELECT table_name FROM information_schema.tables
                   WHERE table_schema='public' AND table_name IN
                     ('student_ai_tutor_usage','ai_tutor_platform_usage','topic_lesson_content',
                      'lesson_practice_questions','student_topic_progress','student_lesson_practice_attempts','student_saved_topics')"""
            ).fetchall()
        self.assertEqual({row[0] for row in names}, {
            "student_ai_tutor_usage","ai_tutor_platform_usage","topic_lesson_content",
            "lesson_practice_questions","student_topic_progress","student_lesson_practice_attempts","student_saved_topics"
        })


    def test_podcast_script_table_exists(self):
        with psycopg.connect(self.dsn) as conn:
            row = conn.execute(
                """SELECT to_regclass('public.podcast_scripts')"""
            ).fetchone()
        self.assertEqual(row[0], "podcast_scripts")

    def test_curriculum_target_version_is_seeded(self):
        with psycopg.connect(self.dsn) as conn:
            row = conn.execute(
                "SELECT status,is_target_version FROM curriculum_versions WHERE version_code='nerdc_ssec_2025'"
            ).fetchone()
        self.assertEqual(row, ("active", True))

    def test_migration_replay_is_idempotent(self):
        self.assertEqual(rehearse(self.dsn), [])

    def test_audit_events_are_append_only(self):
        with psycopg.connect(self.dsn) as conn:
            with conn.transaction():
                row = conn.execute(
                    """INSERT INTO audit_events(event_type,entity_type,entity_id,details)
                       VALUES ('integration.test','test','temporary', '{}'::jsonb)
                       RETURNING id"""
                ).fetchone()
                with self.assertRaises(psycopg.errors.RaiseException):
                    with conn.transaction():
                        conn.execute("UPDATE audit_events SET entity_id='tampered' WHERE id=%s",
                                     (row[0],))


if __name__ == "__main__":
    unittest.main()
