"""Default-deny admin role/capability policy for Learnwise.

This module is a policy primitive, not authentication. Callers must obtain the
admin identity from a verified server-side session and audit authorised actions.
"""
from dataclasses import dataclass


CAPABILITIES = frozenset({
    "curriculum.read", "curriculum.edit", "curriculum.publish",
    "audio.upload", "audio.review",
    "assessment.read", "assessment.edit", "assessment.publish", "assessment.review", "assessment.respond",
    "student.support", "student.read_private",
    "payment.read", "payment.reconcile", "payment.refund",
    "export.request", "export.approve", "export.download",
    "audit.read", "settings.manage",
})

ROLE_CAPABILITIES = {
    "owner": CAPABILITIES,
    "editor": frozenset({
        "curriculum.read", "curriculum.edit",
        "assessment.read", "assessment.edit", "audio.upload",
    }),
    "reviewer": frozenset({
        "curriculum.read", "curriculum.publish", "audio.review",
        "assessment.read", "assessment.publish", "assessment.review",
        "assessment.respond",
    }),
    "support": frozenset({
        "assessment.read", "assessment.respond",
        "student.support",
    }),
    "analyst": frozenset({
        "curriculum.read", "assessment.read",
        "payment.read", "audit.read",
    }),
}


@dataclass(frozen=True)
class AdminPrincipal:
    admin_id: str
    role: str
    is_active: bool


def can(principal, capability):
    """Return False for missing, inactive, unknown or malformed principals."""
    if not isinstance(principal, AdminPrincipal) or principal.is_active is not True:
        return False
    if not isinstance(principal.admin_id, str) or not principal.admin_id.strip():
        return False
    if not isinstance(capability, str) or capability not in CAPABILITIES:
        return False
    return capability in ROLE_CAPABILITIES.get(principal.role, frozenset())


def require(principal, capability):
    if not can(principal, capability):
        raise PermissionError("This account is not authorised to perform that action.")
