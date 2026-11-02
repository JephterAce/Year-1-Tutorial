import unittest

from admin_policy import AdminPrincipal, can, require


class AdminPolicyTests(unittest.TestCase):
    def principal(self, role, active=True):
        return AdminPrincipal("admin-1", role, active)

    def test_owner_has_all_defined_capabilities(self):
        for capability in (
            "curriculum.publish", "assessment.review", "student.read_private",
            "payment.refund", "export.download", "settings.manage",
        ):
            self.assertTrue(can(self.principal("owner"), capability))

    def test_reviewer_can_review_but_not_edit_or_refund(self):
        reviewer = self.principal("reviewer")
        self.assertTrue(can(reviewer, "assessment.review"))
        self.assertTrue(can(reviewer, "curriculum.publish"))
        self.assertFalse(can(reviewer, "curriculum.edit"))
        self.assertFalse(can(reviewer, "payment.refund"))
        self.assertFalse(can(reviewer, "student.read_private"))

    def test_support_is_limited_to_support_work(self):
        support = self.principal("support")
        self.assertTrue(can(support, "student.support"))
        self.assertTrue(can(support, "assessment.respond"))
        self.assertFalse(can(support, "assessment.review"))
        self.assertFalse(can(support, "export.download"))

    def test_analyst_has_read_only_operational_access(self):
        analyst = self.principal("analyst")
        self.assertTrue(can(analyst, "payment.read"))
        self.assertTrue(can(analyst, "audit.read"))
        self.assertFalse(can(analyst, "payment.reconcile"))
        self.assertFalse(can(analyst, "student.read_private"))

    def test_inactive_unknown_and_unknown_capability_fail_closed(self):
        self.assertFalse(can(self.principal("owner", False), "settings.manage"))
        self.assertFalse(can(self.principal("superuser"), "settings.manage"))
        self.assertFalse(can(self.principal("owner"), "system.shell"))

    def test_malformed_capability_fails_closed(self):
        self.assertFalse(can(self.principal("owner"), []))

    def test_require_raises_for_denied_action(self):
        with self.assertRaises(PermissionError):
            require(self.principal("editor"), "curriculum.publish")


if __name__ == "__main__":
    unittest.main()
