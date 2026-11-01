import unittest
from app import app


class ApiSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_catalogue_is_explicitly_demo(self):
        response = self.client.get("/api/v1/catalogue")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["is_demo"])
        self.assertGreaterEqual(len(payload["items"]), 1)

    def test_unknown_route_is_json_404(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
