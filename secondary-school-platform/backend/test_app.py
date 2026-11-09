import os
import unittest
from pathlib import Path
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
        expected_subjects = {
            "English Language",
            "General Mathematics",
            "Further Mathematics",
            "Biology",
            "Chemistry",
            "Physics",
        }
        self.assertEqual(subjects, expected_subjects)
        self.assertEqual(len(payload["items"]), 6)
        self.assertTrue(all(item["demo"] is True for item in payload["items"]))
        self.assertTrue(all(item["term"] == "Term allocation pending" for item in payload["items"]))
        self.assertTrue(all("class_level" not in item for item in payload["items"]))

    def test_demo_catalogue_does_not_claim_class_mapping(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/api/v1/catalogue?class=SS1")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["items"]), 6)
        self.assertTrue(all("class_level" not in item for item in payload["items"]))

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


class StudentUiContractTests(unittest.TestCase):
    def test_student_dashboard_shows_exact_six_subjects(self):
        frontend = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html = frontend.read_text(encoding="utf-8")
        self.assertIn('<small>Subjects available</small><strong id="dashSubjects">—</strong>', html)
        self.assertIn("dashSubjects').textContent=(data.subjects||[]).filter(x=>x.published_lessons>0).length", html)
        for subject in (
            "English Language",
            "General Mathematics",
            "Further Mathematics",
            "Biology",
            "Chemistry",
            "Physics",
        ):
            self.assertEqual(html.count(f"<h3>{subject}</h3>"), 1)

    def test_student_catalogue_uses_safe_dom_text_and_published_api(self):
        frontend = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html = frontend.read_text(encoding="utf-8")
        self.assertIn("fetch('/api/v1/catalogue?'", html)
        self.assertIn("title.textContent=topic.title", html)
        self.assertIn("summary.textContent=topic.summary", html)
        self.assertIn("button.addEventListener('click'", html)
        self.assertIn("Class mapping pending", html)

    def test_student_profile_and_assessment_experience_is_present(self):
        frontend = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html = frontend.read_text(encoding="utf-8")
        for page in ("assessments", "profile"):
            self.assertIn(f'id="{page}"', html)
            self.assertIn(f'data-page="{page}"', html)
        for field in ("profileName", "profileUsername", "profileEmail", "profileClass", "profileBio", "profilePhoto", "profileVisibility"):
            self.assertIn(f'id="{field}"', html)
        self.assertIn("Private profile by default", html)
        self.assertIn("Save profile", html)
        self.assertIn("loadStudentProfile()", html)
        self.assertIn("automatically by the server", html)
        self.assertIn("separate permission", html)

    def test_admin_workspace_has_working_preview_sections(self):
        admin = Path(__file__).resolve().parents[1] / "admin" / "index.html"
        html = admin.read_text(encoding="utf-8")
        for page in ("overview", "curriculum", "studio", "audio", "announcements", "students", "settings"):
            self.assertIn(f'id="{page}"', html)
            self.assertIn(f'data-page="{page}"', html)
        self.assertIn("broadcast-only Channel", html)
        self.assertIn("Manual publishing", html)
        self.assertIn("copyAnnouncement()", html)
        self.assertIn("not connected", html.lower())

    def test_student_catalogue_does_not_invent_class_or_term_mapping(self):
        frontend = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html = frontend.read_text(encoding="utf-8")
        self.assertIn("Class mapping pending", html)
        self.assertIn("Term allocation pending", html)
        self.assertIn('<option value="Term allocation pending">Term allocation pending</option>', html)
        self.assertNotIn("<option>First term</option>", html)
        self.assertNotIn("<option>Second term</option>", html)
        self.assertNotIn("<option>Third term</option>", html)


class DatabaseConfigTests(unittest.TestCase):
    def test_database_url_is_not_hardcoded(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(database.database_url())

    def test_database_url_comes_from_environment(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example"}, clear=True):
            self.assertEqual(database.database_url(), "postgresql://example")


    def test_student_pages_are_served_and_admin_pages_require_session(self):
        client = app.test_client()
        for path in ("/", "/account", "/assessment", "/lesson"):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("text/html", response.content_type)

        login_page = client.get("/admin/login")
        self.assertEqual(login_page.status_code, 200)
        self.assertIn("noindex, nofollow", login_page.headers.get("X-Robots-Tag", ""))
        self.assertIn(b"Administrator workspace", login_page.data)

        for path in ("/admin", "/admin/operations", "/admin/reviews"):
            response = client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response.headers.get("Location"), "/admin/login")

        self.assertEqual(client.get("/api/v1/admin/auth/me").status_code, 401)


    def test_staging_signup_and_checkout_are_disabled_by_default(self):
        with patch.dict("os.environ", {
            "APP_ENV": "staging",
            "STUDENT_REGISTRATION_ENABLED": "0",
            "PAYMENTS_ENABLED": "0",
        }):
            client = app.test_client()
            self.assertEqual(client.post("/api/v1/auth/register", json={}).status_code, 503)
            self.assertEqual(client.post("/api/v1/topics/00000000-0000-0000-0000-000000000001/checkout", json={}).status_code, 503)


class AdminSmtpDiagnosticRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.owner = {
            "admin_id": "00000000-0000-0000-0000-000000000001",
            "email": "admin@example.test",
            "role": "owner",
            "principal": __import__("admin_policy").AdminPrincipal(
                "00000000-0000-0000-0000-000000000001", "owner", True
            ),
        }

    def test_smtp_diagnostic_is_disabled_unless_explicitly_enabled_in_staging(self):
        with patch.dict(os.environ, {"APP_ENV": "staging"}, clear=True):
            response = self.client.post("/api/v1/admin/diagnostics/smtp")
        self.assertEqual(response.status_code, 404)

    def test_smtp_diagnostic_rejects_anonymous_request(self):
        with patch.dict(os.environ, {
            "APP_ENV": "staging", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True), patch("app._current_admin", return_value=None):
            response = self.client.post("/api/v1/admin/diagnostics/smtp")
        self.assertEqual(response.status_code, 401)

    def test_smtp_diagnostic_rejects_non_owner(self):
        reviewer = dict(self.owner)
        reviewer["role"] = "reviewer"
        reviewer["principal"] = __import__("admin_policy").AdminPrincipal(
            reviewer["admin_id"], "reviewer", True
        )
        with patch.dict(os.environ, {
            "APP_ENV": "staging", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True), patch("app._current_admin", return_value=reviewer):
            response = self.client.post(
                "/api/v1/admin/diagnostics/smtp",
                headers={"X-CSRF-Token": "test-csrf"},
            )
        self.assertEqual(response.status_code, 403)

    def test_owner_diagnostic_sends_only_to_signed_in_admin_and_audits(self):
        with patch.dict(os.environ, {
            "APP_ENV": "staging", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True):
            with patch("app._current_admin", return_value=self.owner) as current_admin:
                with patch("admin_auth.reserve_admin_smtp_diagnostic") as throttle:
                    with patch("admin_auth.record_admin_audit") as audit:
                        with patch("identity_email.send_admin_diagnostic") as send:
                            response = self.client.post(
                                "/api/v1/admin/diagnostics/smtp",
                                headers={"X-CSRF-Token": "test-csrf"},
                            )
        self.assertEqual(response.status_code, 202)
        current_admin.assert_called_once_with(require_csrf=True)
        send.assert_called_once_with("admin@example.test")
        throttle.assert_called_once_with("admin@example.test")
        audit.assert_called_once()
        self.assertEqual(audit.call_args.args[1], "smtp_diagnostic_sent")

    def test_smtp_diagnostic_logs_safe_failure_phase_and_exception_class(self):
        with patch.dict(os.environ, {
            "APP_ENV": "staging", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True):
            with patch("app._current_admin", return_value=self.owner):
                with patch("admin_auth.reserve_admin_smtp_diagnostic", side_effect=RuntimeError("sensitive provider detail")):
                    with patch("admin_auth.record_admin_audit"):
                        with self.assertLogs("app", level="WARNING") as captured:
                            response = self.client.post(
                                "/api/v1/admin/diagnostics/smtp",
                                headers={"X-CSRF-Token": "test-csrf"},
                            )
        self.assertEqual(response.status_code, 503)
        self.assertTrue(any(
            "phase=rate_limit_reservation" in line and "category=internal_error" in line
            for line in captured.output
        ))
        self.assertFalse(any("sensitive provider detail" in line for line in captured.output))


    def test_smtp_diagnostic_returns_safe_provider_status_and_code(self):
        from identity_email import BrevoDeliveryError
        with patch.dict(os.environ, {
            "APP_ENV": "staging", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True):
            with patch("app._current_admin", return_value=self.owner):
                with patch("admin_auth.reserve_admin_smtp_diagnostic"):
                    with patch("admin_auth.record_admin_audit") as audit:
                        with patch("identity_email.send_admin_diagnostic",
                                   side_effect=BrevoDeliveryError(
                                       "provider_rejected_request", 401, "unauthorized"
                                   )):
                            response = self.client.post(
                                "/api/v1/admin/diagnostics/smtp",
                                headers={"X-CSRF-Token": "test-csrf"},
                            )
        self.assertEqual(response.status_code, 503)
        payload = response.get_json()["diagnostic"]
        self.assertEqual(payload["http_status"], 401)
        self.assertEqual(payload["provider_error_code"], "unauthorized")
        self.assertEqual(payload["failure_category"], "provider_rejected_request")
        self.assertNotIn("api_key", str(response.get_json()).lower())
        self.assertNotIn("admin@example.test", str(response.get_json()))
        self.assertEqual(audit.call_args.args[3], "admin")
        self.assertEqual(audit.call_args.args[5]["http_status"], 401)

    def test_smtp_diagnostic_is_never_available_outside_staging(self):
        with patch.dict(os.environ, {
            "APP_ENV": "production", "ADMIN_SMTP_DIAGNOSTIC_ENABLED": "1"
        }, clear=True):
            response = self.client.post("/api/v1/admin/diagnostics/smtp")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
