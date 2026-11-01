import os
import unittest
from unittest.mock import patch

from app import app
import database


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_demo_mode(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["mode"], "demo")

    def test_demo_catalogue_is_labelled(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/api/v1/catalogue")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["is_demo"])
        self.assertGreaterEqual(len(payload["items"]), 1)
        subjects = {item["subject"] for item in payload["items"]}
        self.assertIn("English Language", subjects)
        self.assertIn("General Mathematics", subjects)
        self.assertIn("Further Mathematics", subjects)

    def test_invalid_class_rejected(self):
        response = self.client.get("/api/v1/catalogue?class=Year7")
        self.assertEqual(response.status_code, 400)

    def test_invalid_term_rejected(self):
        response = self.client.get("/api/v1/catalogue?term=4")
        self.assertEqual(response.status_code, 400)

    def test_unknown_route_is_json_404(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "not_found")


class DatabaseConfigTests(unittest.TestCase):
    def test_database_url_is_not_hardcoded(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(database.database_url())

    def test_database_url_comes_from_environment(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example"}, clear=True):
            self.assertEqual(database.database_url(), "postgresql://example")


if __name__ == "__main__":
    unittest.main()
