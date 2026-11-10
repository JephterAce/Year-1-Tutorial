"""Validation and field policy for student-data export requests.

This module deliberately does not expose an HTTP endpoint. Export requests must
be called only after authentication, permission checks and audit setup exist.
"""
from dataclasses import dataclass
from datetime import date
import re

ALLOWED_FORMATS = frozenset({"csv", "json"})
ALLOWED_CLASSES = frozenset({"SS1", "SS2", "SS3"})
MAX_BULK_ROWS = 1_000
MAX_DATE_RANGE_DAYS = 366

# Explicit allowlist: never export credentials, tokens, answer keys or provider secrets.
STUDENT_EXPORT_FIELDS = frozenset({
    "student_id", "email", "display_name", "username", "class_level",
    "bio", "profile_visibility", "created_at", "updated_at",
})
PROGRESS_EXPORT_FIELDS = frozenset({
    "topic_id", "asset_id", "position_seconds", "completed_at", "updated_at",
})
ASSESSMENT_EXPORT_FIELDS = frozenset({
    "assessment_id", "attempt_id", "version", "status", "started_at",
    "submitted_at", "score", "question_id", "answer", "is_correct",
    "feedback",
})
PAYMENT_EXPORT_FIELDS = frozenset({
    "topic_id", "provider", "provider_reference", "amount_kobo",
    "currency", "status", "verified_at", "created_at",
})
NEVER_EXPORT_FIELDS = frozenset({
    "password_hash", "password", "session_token", "reset_token",
    "verification_token", "answer_key", "provider_payload", "secret",
})


@dataclass(frozen=True)
class ExportRequest:
    scope: str
    export_format: str
    student_id: str | None = None
    class_levels: tuple[str, ...] = ()
    subject_slugs: tuple[str, ...] = ()
    date_from: str | None = None
    date_to: str | None = None


def _iso_date(value: str | None, field: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD).") from None


def validate_export_request(payload: dict) -> ExportRequest:
    if not isinstance(payload, dict):
        raise ValueError("Export request must be an object.")
    scope = payload.get("scope")
    fmt = payload.get("format")
    if scope not in {"individual", "bulk"}:
        raise ValueError("Scope must be individual or bulk.")
    if fmt not in ALLOWED_FORMATS:
        raise ValueError("Format must be csv or json.")

    student_id = payload.get("student_id")
    if scope == "individual":
        if not isinstance(student_id, str) or not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}",
            student_id,
        ):
            raise ValueError("A valid student ID is required for individual export.")
    elif student_id is not None:
        raise ValueError("Bulk exports cannot target a single student.")

    classes = payload.get("class_levels", [])
    subjects = payload.get("subject_slugs", [])
    if not isinstance(classes, list) or any(c not in ALLOWED_CLASSES for c in classes):
        raise ValueError("Class filters may contain only SS1, SS2 and SS3.")
    if not isinstance(subjects, list) or any(
        not isinstance(s, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s)
        for s in subjects
    ):
        raise ValueError("Subject filters must be valid subject slugs.")

    start = _iso_date(payload.get("date_from"), "date_from")
    end = _iso_date(payload.get("date_to"), "date_to")
    if bool(start) != bool(end):
        raise ValueError("Both date_from and date_to must be supplied together.")
    if start and (end < start or (end - start).days > MAX_DATE_RANGE_DAYS):
        raise ValueError("Date range is invalid or exceeds 366 days.")

    return ExportRequest(
        scope=scope,
        export_format=fmt,
        student_id=student_id,
        class_levels=tuple(sorted(set(classes))),
        subject_slugs=tuple(sorted(set(subjects))),
        date_from=start.isoformat() if start else None,
        date_to=end.isoformat() if end else None,
    )


def filter_export_fields(records: list[dict], allowed_fields: frozenset[str]) -> list[dict]:
    """Return only explicitly approved fields, preserving requested record order."""
    safe = []
    for record in records:
        safe.append({key: value for key, value in record.items() if key in allowed_fields})
    return safe
