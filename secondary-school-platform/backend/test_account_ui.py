import unittest
from pathlib import Path


class StudentAccountUiTests(unittest.TestCase):
    def test_account_page_connects_all_identity_flows(self):
        page = Path(__file__).resolve().parents[1] / "frontend" / "account.html"
        html = page.read_text(encoding="utf-8")
        for route in (
            "/api/v1/auth/register", "/api/v1/auth/login",
            "/api/v1/auth/verify-email", "/api/v1/auth/password-reset",
            "/api/v1/auth/password-reset/complete", "/api/v1/auth/me",
            "/api/v1/auth/logout",
        ):
            self.assertIn(route, html)
        self.assertIn('name="accept_terms"', html)
        self.assertIn('name="accept_privacy"', html)
        self.assertIn('name="class_level"', html)
        self.assertIn('name="referrer" content="no-referrer"', html)
        self.assertIn("history.replaceState", html)
        self.assertIn("X-CSRF-Token", html)

    def test_account_fields_have_accessible_names_and_autocomplete(self):
        page = Path(__file__).resolve().parents[1] / "frontend" / "account.html"
        html = page.read_text(encoding="utf-8")
        for label in (
            'aria-label="Display name"', 'aria-label="Username"',
            'aria-label="Registration email address"', 'aria-label="Class level"',
            'aria-label="Create password"', 'aria-label="Sign-in email address"',
            'aria-label="Sign-in password"', 'aria-label="Password reset email address"',
            'aria-label="New password"',
        ):
            self.assertIn(label, html)
        self.assertIn("autocomplete=\"current-password\"", html)
        self.assertIn("autocomplete=\"new-password\"", html)

    def test_password_reset_shows_pending_and_completion_feedback(self):
        page = Path(__file__).resolve().parents[1] / "frontend" / "account.html"
        html = page.read_text(encoding="utf-8")
        self.assertIn("Submitting your request…", html)
        self.assertIn("We could not complete the request right now. Check your connection and try again.", html)
        self.assertIn("button.disabled=true", html)
        self.assertIn("button.disabled=false", html)
        self.assertIn("Updating your password…", html)
        self.assertIn("Password updated. Sign in with your new password.", html)
        self.assertIn("If an eligible account exists, reset instructions will be sent.", html)

    def test_dashboard_links_to_account_page(self):
        page = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html = page.read_text(encoding="utf-8")
        self.assertIn('href="account.html"', html)


if __name__ == "__main__":
    unittest.main()
