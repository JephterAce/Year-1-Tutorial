import csv
import json
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from export_serialization import (
    ExportSerializationError, serialise_csv, serialise_json,
)


class ExportSerialisationTests(unittest.TestCase):
    def setUp(self):
        self.allowed = frozenset({"name", "amount", "created", "metadata"})

    def test_json_uses_allowlist_and_normalises_types(self):
        student_id = UUID("12345678-1234-4234-8234-123456789abc")
        result = json.loads(serialise_json([{
            "name": "Ada", "amount": Decimal("12.50"),
            "created": date(2026, 1, 2), "metadata": {"id": student_id},
            "password_hash": "never",
        }], self.allowed))
        self.assertEqual(result[0]["amount"], "12.50")
        self.assertEqual(result[0]["created"], "2026-01-02")
        self.assertNotIn("password_hash", result[0])
        self.assertEqual(result[0]["metadata"]["id"], str(student_id))

    def test_csv_neutralises_formula_injection(self):
        result = serialise_csv([
            {"name": "=HYPERLINK(\"https://bad.example\")", "amount": 4},
            {"name": "  @SUM(A1:A2)", "amount": 5},
            {"name": "Normal learner", "amount": 6, "password_hash": "hidden"},
        ], self.allowed)
        rows = list(csv.DictReader(result.splitlines()))
        self.assertEqual(rows[0]["name"][0], "'")
        self.assertEqual(rows[1]["name"], "'  @SUM(A1:A2)")
        self.assertEqual(rows[2]["name"], "Normal learner")
        self.assertNotIn("password_hash", result)

    def test_csv_serialises_nested_values_and_decimal(self):
        result = serialise_csv([{"amount": Decimal("1.25"),
                                 "metadata": {"ok": True}}], self.allowed)
        rows = list(csv.DictReader(result.splitlines()))
        self.assertEqual(rows[0]["amount"], "1.25")
        self.assertEqual(json.loads(rows[0]["metadata"]), {"ok": True})

    def test_rejects_non_object_records_and_unsupported_values(self):
        with self.assertRaises(ExportSerializationError):
            serialise_json([None], self.allowed)
        with self.assertRaises(ExportSerializationError):
            serialise_json([{"name": object()}], self.allowed)

    def test_empty_export_is_valid(self):
        self.assertEqual(serialise_json([], self.allowed), "[]")
        self.assertEqual(serialise_csv([], self.allowed), "")


if __name__ == "__main__":
    unittest.main()
