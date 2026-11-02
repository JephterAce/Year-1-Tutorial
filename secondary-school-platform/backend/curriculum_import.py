"""Evidence-first curriculum import validation for Learnwise.

This module validates metadata rows; it does not scrape protected portals, infer
curriculum topics, or grant rights to reproduce NERDC materials.
"""
from dataclasses import dataclass
from urllib.parse import urlparse

TARGET_VERSION = "nerdc_ssec_2025"
CLASSES = {"SS1", "SS2", "SS3"}
SUBJECTS = {
    "english-language", "general-mathematics", "further-mathematics",
    "biology", "chemistry", "physics",
}
REVIEW_STATES = {
    "unresearched", "source_captured", "mapped", "term_pending",
    "teacher_review", "approved", "published", "rejected",
}
TERM_STATES = {
    "official_term_allocation", "school_scheme_verified",
    "school_scheme_required", "not_assigned",
}
APPROVABLE_SOURCE_KINDS = {"official_nerdc", "school_scheme", "teacher_reference"}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple
    warnings: tuple


def _http_url(value):
    try:
        parsed = urlparse(value or "")
        return parsed.scheme == "https" and bool(parsed.netloc)
    except (TypeError, ValueError):
        return False


def validate_curriculum_row(row, *, for_publication=False):
    """Validate one import row and fail closed for publication."""
    errors, warnings = [], []
    required = ("class_level", "subject_slug", "title", "curriculum_version",
                "source_title", "source_url", "source_kind", "review_status",
                "term_mapping_status")
    for field in required:
        if not str(row.get(field, "")).strip():
            errors.append(f"{field} is required")

    if row.get("class_level") and row["class_level"] not in CLASSES:
        errors.append("class_level must be SS1, SS2 or SS3")
    if row.get("subject_slug") and row["subject_slug"] not in SUBJECTS:
        errors.append("subject_slug is outside the approved six-subject product scope")
    if row.get("curriculum_version") and row["curriculum_version"] != TARGET_VERSION:
        errors.append("Only the target revised 2025 NERDC SSEC version is accepted")
    if row.get("source_url") and not _http_url(row["source_url"]):
        errors.append("source_url must be an HTTPS source")
    if row.get("source_kind") and row["source_kind"] not in APPROVABLE_SOURCE_KINDS:
        errors.append("source_kind is not recognised")
    if row.get("review_status") and row["review_status"] not in REVIEW_STATES:
        errors.append("review_status is not recognised")
    if row.get("term_mapping_status") and row["term_mapping_status"] not in TERM_STATES:
        errors.append("term_mapping_status is not recognised")

    if row.get("term_mapping_status") == "school_scheme_verified" and not str(row.get("school_scheme_name", "")).strip():
        errors.append("school_scheme_name is required for school-scheme term mapping")
    if row.get("term_mapping_status") == "official_term_allocation":
        if row.get("source_kind") != "official_nerdc":
            errors.append("official term allocation requires an official NERDC source")
    if row.get("learning_outcomes") and not isinstance(row["learning_outcomes"], (list, tuple)):
        errors.append("learning_outcomes must be a list of source-grounded statements")

    if not row.get("source_section"):
        warnings.append("source_section is missing; reviewers may not be able to locate the evidence")
    if row.get("term_mapping_status") in {"school_scheme_required", "not_assigned"}:
        warnings.append("Term placement remains unassigned; do not display this as a term-specific lesson")

    if for_publication:
        if row.get("review_status") != "approved":
            errors.append("publication requires approved review status")
        if not str(row.get("reviewed_by", "")).strip():
            errors.append("publication requires a named teacher/reviewer")
        if not str(row.get("reviewed_at", "")).strip():
            errors.append("publication requires a review timestamp")
        if not str(row.get("source_section", "")).strip():
            errors.append("publication requires a precise source section/page/topic reference")
        if not str(row.get("curriculum_evidence_note", "")).strip():
            errors.append("publication requires an evidence note")
        if row.get("source_kind") == "school_scheme" and not str(row.get("school_scheme_name", "")).strip():
            errors.append("school-scheme publication requires the scheme name")
        if row.get("licence_status", "metadata_only") not in {"metadata_only", "permission_granted"}:
            errors.append("publication requires a known rights status")
        if row.get("term_mapping_status") == "school_scheme_required":
            errors.append("term-specific publication is blocked until a school scheme is verified")

    return ValidationResult(not errors, tuple(errors), tuple(warnings))


def validate_import(rows, *, for_publication=False):
    results = [validate_curriculum_row(row, for_publication=for_publication) for row in rows]
    return {
        "valid": all(result.valid for result in results),
        "row_count": len(results),
        "error_count": sum(len(result.errors) for result in results),
        "warning_count": sum(len(result.warnings) for result in results),
        "rows": results,
    }

import csv
import io
import json


def parse_csv_import(csv_text):
    """Parse the supplied CSV template, decoding JSON learning outcomes safely."""
    if not isinstance(csv_text, str):
        raise ValueError("CSV input must be text")
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        raise ValueError("CSV header row is required")
    rows = []
    for line_number, raw in enumerate(reader, start=2):
        row = {key: (value.strip() if isinstance(value, str) else value)
               for key, value in raw.items() if key}
        outcomes = row.get("learning_outcomes", "")
        if outcomes:
            try:
                row["learning_outcomes"] = json.loads(outcomes)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"learning_outcomes on CSV line {line_number} must be a JSON array"
                ) from exc
        else:
            row["learning_outcomes"] = []
        rows.append(row)
    return rows


def validate_csv_import(csv_text, *, for_publication=False):
    """Parse and validate a CSV batch without writing to the database."""
    rows = parse_csv_import(csv_text)
    return validate_import(rows, for_publication=for_publication)
