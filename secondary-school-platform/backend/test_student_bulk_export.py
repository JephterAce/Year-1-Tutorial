import csv
import hashlib
import io
import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from student_bulk_export import (
    ExportWorkerError, _export_chunks, _multipart_upload, _student_query, _storage,
)


class FakeS3:
    def __init__(self):
        self.parts = []
        self.objects = {}
        self.aborted = False
        self.completed = False

    def create_multipart_upload(self, **kwargs):
        self.key = kwargs["Key"]
        return {"UploadId": "upload-1"}

    def upload_part(self, **kwargs):
        self.parts.append(kwargs["Body"])
        return {"ETag": f"etag-{kwargs['PartNumber']}"}

    def complete_multipart_upload(self, **kwargs):
        self.completed = True
        self.objects[self.key] = b"".join(self.parts)

    def abort_multipart_upload(self, **kwargs):
        self.aborted = True

    def put_object(self, **kwargs):
        self.objects[kwargs["Key"]] = kwargs["Body"]


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.itersize = None
        self.query = None
        self.params = None
        self.closed = False

    def execute(self, query, params):
        self.query, self.params = query, params

    def __iter__(self):
        return iter(self.rows)

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, rows):
        self.fake_cursor = FakeCursor(rows)

    def cursor(self, name=None):
        self.cursor_name = name
        return self.fake_cursor


class BulkExportWorkerTests(unittest.TestCase):
    def test_bulk_query_is_parameterised_and_scope_bounded(self):
        query, params = _student_query({
            "class_levels": ["SS1", "SS3"],
            "date_from": "2026-01-01",
            "date_to": "2026-03-31",
        })
        self.assertIn("class_level = ANY(%s)", query)
        self.assertIn("created_at >= %s::date", query)
        self.assertIn("created_at < (%s::date + interval '1 day')", query)
        self.assertEqual(params, [["SS1", "SS3"], "2026-01-01", "2026-03-31"])
        self.assertNotIn("2026-01-01", query)

    def test_json_export_streams_one_complete_student_record_per_line(self):
        student_id = UUID("12345678-1234-4234-8234-123456789abc")
        conn = FakeConnection([{"id": student_id}])
        job = {"export_scope": "individual", "target_student_id": str(student_id), "export_format": "json", "filters": {}}
        payload = {
            "export_version": "1.0",
            "student": {"id": str(student_id), "email": "learner@example.test"},
            "security_notice": "credentials and answer keys excluded",
        }
        with patch("student_bulk_export.build_student_export", return_value=payload):
            chunks = list(_export_chunks(conn, job, datetime.now(timezone.utc)))
        self.assertEqual(len(chunks), 1)
        self.assertEqual(json.loads(chunks[0].decode("utf-8")), payload)
        self.assertTrue(conn.fake_cursor.closed)
        self.assertEqual(conn.cursor_name, "think_tank_export_students")

    def test_csv_export_neutralises_formula_prefixes_and_embeds_nested_record(self):
        student_id = UUID("12345678-1234-4234-8234-123456789abc")
        conn = FakeConnection([{"id": student_id}])
        payload = {
            "student": {
                "id": str(student_id), "email": "=HYPERLINK('bad')",
                "display_name": "Learner", "username": "learner", "class_level": "SS1",
            },
            "assessment_answers": [],
        }
        with patch("student_bulk_export.build_student_export", return_value=payload):
            chunks = list(_export_chunks(conn, {"export_scope": "individual", "target_student_id": str(student_id), "export_format": "csv", "filters": {}},
                                         datetime.now(timezone.utc)))
        rows = list(csv.DictReader(io.StringIO(b"".join(chunks).decode("utf-8"))))
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["email"].startswith("'"))
        self.assertEqual(json.loads(rows[0]["record_json"])["assessment_answers"], [])

    def test_multipart_upload_hashes_and_completes_stream(self):
        client = FakeS3()
        checksum, size = _multipart_upload(
            client, "private-exports", "exports/test/data.jsonl",
            [b'{"a":', b'1}\n'], "application/x-ndjson", "job-1",
        )
        self.assertEqual(checksum, hashlib.sha256(b'{"a":1}\n').hexdigest())
        self.assertEqual(size, len(b'{"a":1}\n'))
        self.assertTrue(client.completed)
        self.assertFalse(client.aborted)
        self.assertEqual(client.objects["exports/test/data.jsonl"], b'{"a":1}\n')

    def test_empty_export_creates_a_zero_byte_private_object(self):
        client = FakeS3()
        checksum, size = _multipart_upload(
            client, "private-exports", "exports/empty/data.jsonl",
            [], "application/x-ndjson", "job-empty",
        )
        self.assertEqual(size, 0)
        self.assertEqual(checksum, hashlib.sha256(b"").hexdigest())
        self.assertTrue(client.aborted)
        self.assertEqual(client.objects["exports/empty/data.jsonl"], b"")

    def test_storage_fails_closed_without_a_dedicated_private_bucket(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ExportWorkerError):
                _storage()

    def test_export_storage_must_not_reuse_audio_bucket(self):
        values = {
            "DATA_EXPORT_AWS_ACCESS_KEY_ID": "test-key",
            "DATA_EXPORT_AWS_SECRET_ACCESS_KEY": "test-secret",
            "DATA_EXPORT_AWS_ENDPOINT_URL_S3": "https://storage.example.test",
            "DATA_EXPORT_AWS_REGION": "eu-central-1",
            "DATA_EXPORT_STORAGE_BUCKET": "shared-audio-bucket",
            "AUDIO_STORAGE_BUCKET": "shared-audio-bucket",
        }
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ExportWorkerError):
                _storage()


if __name__ == "__main__":
    unittest.main()
