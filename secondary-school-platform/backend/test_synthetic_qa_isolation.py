import unittest
from unittest.mock import MagicMock

from student_bulk_export import _student_query
from student_data_export import build_student_export, StudentExportError


class SyntheticQADataIsolationTests(unittest.TestCase):
    def test_bulk_export_always_excludes_synthetic_identities(self):
        query, params = _student_query({})
        self.assertIn("is_synthetic_qa=false", query)
        self.assertEqual(params, [])

    def test_filtered_bulk_export_keeps_synthetic_exclusion(self):
        query, params = _student_query({"class_levels": ["SS1"]})
        self.assertIn("is_synthetic_qa=false", query)
        self.assertIn("class_level = ANY(%s)", query)
        self.assertEqual(params, [["SS1"]])

    def test_individual_self_export_rejects_synthetic_identity(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        with self.assertRaises(StudentExportError):
            build_student_export("synthetic-student-id", conn=conn)
        sql, params = conn.execute.call_args.args
        self.assertIn("is_synthetic_qa=false", sql)
        self.assertEqual(params, ("synthetic-student-id",))


if __name__ == "__main__":
    unittest.main()
