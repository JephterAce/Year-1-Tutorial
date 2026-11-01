import os
import unittest
from unittest.mock import patch

import database


class DatabaseConfigTests(unittest.TestCase):
    def test_database_url_is_not_hardcoded(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(database.database_url())

    def test_database_url_comes_from_environment(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example"}, clear=True):
            self.assertEqual(database.database_url(), "postgresql://example")


if __name__ == "__main__":
    unittest.main()
