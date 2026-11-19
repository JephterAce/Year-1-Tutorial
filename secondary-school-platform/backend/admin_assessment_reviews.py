"""Least-privilege admin review workflow for student assessment issue reports."""
from uuid import UUID

from flask import Blueprint, jsonify, request

from admin_policy import require
from database import connection

admin_reviews = Blueprint("admin_reviews", __name__)


def _principal(require_csrf=False):
    from admin_auth import authenticate_admin, validate_admin_csrf
    session = authenticate_admin(request.cookies.get("learnwise_admin_session"))
    if not session:
        return None
    if require_csrf and not validate_admin_csrf(
        session, request.headers.get("X-CSRF-Token", "")
    ):
        return None
    return session


def list_review_queue(principal, status="submitted", limit=50):
    require(principal, "assessment.review")
    if status not in {"submitted", "under_review", "resolved", "dismissed", "all"}:
        raise ValueError("Unsupported report status.")
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("Limit must be an integer.")
    limit = max(1, min(limit, 100))
    where = "" if status == "all" else "WHERE r.status=%s"
    params = (limit,) if status == "all" else (status, limit)
    with connection() as conn:
        rows = conn.execute(
            f"""SELECT r.id,r.attempt_id,r.question_id,r.issue_type,r.details,r.status,
                       r.reviewer_note,r.created_at,r.reviewed_at,
                       a.assessment_id
                FROM assessment_issue_reports r
                JOIN assessment_attempts a ON a.id=r.attempt_id
                {where}
                ORDER BY r.created_at ASC,r.id ASC
                LIMIT %s""",
            params,
        ).fetchall()
    return [{
        "id": str(row["id"]), "attempt_id": str(row["attempt_id"]),
        "question_id": str(row["question_id"]) if row["question_id"] else None,
        "assessment_id": str(row["assessment_id"]),
        "issue_type": row["issue_type"], "details": row["details"],
        "status": row["status"], "reviewer_note": row["reviewer_note"],
        "created_at": row["created_at"].isoformat(),
        "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] else None,
    } for row in rows]


def review_report(principal, report_id, status, note):
    require(principal, "assessment.respond")
    try:
        report_id = str(UUID(report_id))
    except (TypeError, ValueError, AttributeError):
        raise ValueError("Invalid report identifier.") from None
    if status not in {"under_review", "resolved", "dismissed"}:
        raise ValueError("Unsupported review action.")
    if not isinstance(note, str):
        raise ValueError("A reviewer note is required.")
    note = " ".join(note.split())
    if not 10 <= len(note) <= 2000:
        raise ValueError("Reviewer notes must be 10–2,000 characters.")

    admin_id = principal.admin_id
    with connection() as conn:
        report = conn.execute(
            """SELECT id,status,issue_type FROM assessment_issue_reports
               WHERE id=%s FOR UPDATE""", (report_id,)
        ).fetchone()
        if not report:
            return None
        current = report["status"]
        allowed = {
            "submitted": {"under_review", "resolved", "dismissed"},
            "under_review": {"resolved", "dismissed"},
        }
        if status not in allowed.get(current, set()):
            raise ValueError("This report has already reached a terminal state or cannot take that transition.")
        updated = conn.execute(
            """UPDATE assessment_issue_reports
               SET status=%s,reviewer_admin_id=%s,reviewer_note=%s,reviewed_at=now()
               WHERE id=%s
               RETURNING id,status,reviewer_note,reviewed_at""",
            (status, admin_id, note, report_id),
        ).fetchone()
        # Audit in the same transaction as the review decision.
        from psycopg.types.json import Jsonb
        conn.execute(
            """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
               VALUES (%s,'assessment_issue.reviewed','assessment_issue_report',%s,%s)""",
            (admin_id, report_id, Jsonb({
                "from_status": current, "to_status": status,
                "issue_type": report["issue_type"],
            })),
        )
    return {
        "id": str(updated["id"]), "status": updated["status"],
        "reviewer_note": updated["reviewer_note"],
        "reviewed_at": updated["reviewed_at"].isoformat(),
    }


@admin_reviews.get("/api/v1/admin/assessment-issues")
def admin_assessment_issue_queue():
    session = _principal()
    if not session:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        items = list_review_queue(
            session["principal"], request.args.get("status", "submitted"),
            int(request.args.get("limit", "50")),
        )
        return jsonify({"items": items}), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_queue_filter"}), 400
    except Exception:
        return jsonify({"error": "review_queue_unavailable"}), 503


@admin_reviews.post("/api/v1/admin/assessment-issues/<report_id>/review")
def admin_review_assessment_issue(report_id):
    session = _principal(require_csrf=True)
    if not session:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        result = review_report(
            session["principal"], report_id, data.get("status"), data.get("reviewer_note")
        )
        if result is None:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"report": result}), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except ValueError as exc:
        return jsonify({"error": "invalid_review", "message": str(exc)}), 400
    except Exception:
        return jsonify({"error": "review_unavailable"}), 503
