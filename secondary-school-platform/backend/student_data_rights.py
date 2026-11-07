"""Student data-rights intake and audited administrator triage.

Requests are tracked, not automatically executed. In particular, a deletion
request never deletes a student account or records from this endpoint.
"""
from uuid import UUID

from flask import Blueprint, current_app, jsonify, request
from psycopg.types.json import Jsonb
from psycopg.errors import UniqueViolation

from database import connection
from admin_policy import require

data_rights = Blueprint("data_rights", __name__)


def _student(require_csrf=False):
    from app import _current_student
    return _current_student(require_csrf=require_csrf)


def _admin(capability, csrf=False):
    from admin_auth import authenticate_admin, validate_admin_csrf
    session = authenticate_admin(request.cookies.get("learnwise_admin_session"))
    if not session:
        return None, (jsonify({"error": "unauthenticated"}), 401)
    if csrf and not validate_admin_csrf(session, request.headers.get("X-CSRF-Token", "")):
        return None, (jsonify({"error": "csrf_failed"}), 401)
    try:
        require(session["principal"], capability)
    except PermissionError:
        return None, (jsonify({"error": "forbidden"}), 403)
    return session, None


def _uuid(value):
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        return None


@data_rights.get("/api/v1/student/data-export")
def download_student_data_export():
    student = _student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    from student_data_export import build_student_export, StudentExportError
    try:
        payload = build_student_export(student["student_id"])
        with connection() as conn:
            conn.execute(
                """INSERT INTO audit_events(student_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'student.data_export.downloaded','student_data_export','self','{}'::jsonb)""",
                (student["student_id"],),
            )
        response = jsonify(payload)
        response.headers["Content-Disposition"] = 'attachment; filename="think-tank-my-data.json"'
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        return response, 200
    except StudentExportError:
        return jsonify({"error": "student_export_unavailable"}), 404
    except Exception:
        current_app.logger.exception("Student self-service export failed")
        return jsonify({"error": "student_export_unavailable"}), 503


@data_rights.get("/api/v1/student/data-rights/requests")
def list_student_requests():
    student = _student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        with connection() as conn:
            rows = conn.execute(
                """SELECT id,request_type,status,request_note,resolution_note,
                          created_at,updated_at,reviewed_at,resolved_at
                   FROM student_data_rights_requests
                   WHERE student_id=%s ORDER BY created_at DESC LIMIT 50""",
                (student["student_id"],),
            ).fetchall()
        return jsonify({"items": [{
            "id": str(r["id"]), "request_type": r["request_type"], "status": r["status"],
            "request_note": r["request_note"], "resolution_note": r["resolution_note"],
            "created_at": r["created_at"].isoformat(), "updated_at": r["updated_at"].isoformat(),
            "reviewed_at": r["reviewed_at"].isoformat() if r["reviewed_at"] else None,
            "resolved_at": r["resolved_at"].isoformat() if r["resolved_at"] else None,
        } for r in rows]}), 200
    except Exception:
        current_app.logger.exception("Student data-rights list failed")
        return jsonify({"error": "data_rights_unavailable"}), 503


@data_rights.post("/api/v1/student/data-rights/requests")
def create_student_request():
    student = _student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    request_type = data.get("request_type")
    note = data.get("request_note")
    if request_type not in {"access_export", "correction", "deletion", "restriction"}:
        return jsonify({"error": "invalid_request_type"}), 400
    if note is not None and (not isinstance(note, str) or len(note.strip()) > 2000):
        return jsonify({"error": "invalid_request_note"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """INSERT INTO student_data_rights_requests(student_id,request_type,request_note)
                   VALUES (%s,%s,%s) RETURNING id,request_type,status,created_at""",
                (student["student_id"], request_type, note.strip() if note else None),
            ).fetchone()
            conn.execute(
                """INSERT INTO audit_events(student_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'student.data_rights.requested','data_rights_request',%s,%s)""",
                (student["student_id"], str(row["id"]), Jsonb({"request_type": request_type})),
            )
            if request_type == "access_export":
                conn.execute(
                    "UPDATE students SET data_export_requested_at=now() WHERE id=%s",
                    (student["student_id"],),
                )
            elif request_type == "deletion":
                conn.execute(
                    "UPDATE students SET deletion_requested_at=now() WHERE id=%s",
                    (student["student_id"],),
                )
        return jsonify({"request": {
            "id": str(row["id"]), "request_type": row["request_type"],
            "status": row["status"], "created_at": row["created_at"].isoformat(),
        }}), 201
    except UniqueViolation:
        return jsonify({"error": "request_already_open"}), 409
    except Exception:
        current_app.logger.exception("Student data-rights request failed")
        return jsonify({"error": "data_rights_request_failed"}), 503


@data_rights.post("/api/v1/student/data-rights/requests/<request_id>/withdraw")
def withdraw_student_request(request_id):
    student = _student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    request_id = _uuid(request_id)
    if not request_id:
        return jsonify({"error": "invalid_request_id"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """UPDATE student_data_rights_requests SET status='withdrawn',updated_at=now()
                   WHERE id=%s AND student_id=%s
                     AND status IN ('submitted','under_review','awaiting_information')
                   RETURNING id""",
                (request_id, student["student_id"]),
            ).fetchone()
            if not row:
                return jsonify({"error": "request_not_withdrawable"}), 409
            conn.execute(
                """INSERT INTO audit_events(student_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'student.data_rights.withdrawn','data_rights_request',%s,'{}'::jsonb)""",
                (student["student_id"], request_id),
            )
        return jsonify({"withdrawn": True, "request_id": request_id}), 200
    except Exception:
        current_app.logger.exception("Student data-rights withdrawal failed")
        return jsonify({"error": "data_rights_withdrawal_failed"}), 503


@data_rights.get("/api/v1/admin/data-rights/requests")
def admin_list_requests():
    session, error = _admin("student.support")
    if error:
        return error
    try:
        limit = max(1, min(int(request.args.get("limit", "50")), 100))
        with connection() as conn:
            rows = conn.execute(
                """SELECT r.id,r.request_type,r.status,r.request_note,r.resolution_note,
                          r.created_at,r.updated_at,s.id AS student_id,s.email,
                          s.display_name,s.class_level
                   FROM student_data_rights_requests r
                   JOIN students s ON s.id=r.student_id
                   ORDER BY CASE WHEN r.status IN ('submitted','under_review','awaiting_information') THEN 0 ELSE 1 END,
                            r.created_at ASC LIMIT %s""",
                (limit,),
            ).fetchall()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.data_rights.viewed','data_rights_requests','list-view',%s)""",
                (session["admin_id"], Jsonb({"returned_count": len(rows)})),
            )
        return jsonify({"items": [{
            "id": str(r["id"]), "request_type": r["request_type"], "status": r["status"],
            "request_note": r["request_note"], "resolution_note": r["resolution_note"],
            "created_at": r["created_at"].isoformat(), "updated_at": r["updated_at"].isoformat(),
            "student": {"id": str(r["student_id"]), "email": r["email"],
                        "display_name": r["display_name"], "class_level": r["class_level"]},
        } for r in rows]}), 200
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_limit"}), 400
    except Exception:
        current_app.logger.exception("Admin data-rights queue failed")
        return jsonify({"error": "admin_data_rights_unavailable"}), 503


@data_rights.post("/api/v1/admin/data-rights/requests/<request_id>/review")
def admin_review_request(request_id):
    session, error = _admin("student.support", csrf=True)
    if error:
        return error
    request_id = _uuid(request_id)
    if not request_id:
        return jsonify({"error": "invalid_request_id"}), 400
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    note = data.get("resolution_note")
    if status not in {"under_review", "awaiting_information", "resolved", "declined"}:
        return jsonify({"error": "invalid_request_status"}), 400
    if status in {"resolved", "declined"} and (not isinstance(note, str) or len(note.strip()) < 10 or len(note) > 2000):
        return jsonify({"error": "resolution_note_required"}), 400
    try:
        with connection() as conn:
            row = conn.execute(
                """UPDATE student_data_rights_requests
                   SET status=%s,resolution_note=%s,reviewed_by_admin_id=%s,
                       reviewed_at=now(),resolved_at=CASE WHEN %s IN ('resolved','declined') THEN now() ELSE NULL END,
                       updated_at=now()
                   WHERE id=%s AND status IN ('submitted','under_review','awaiting_information')
                   RETURNING id,student_id,request_type,status""",
                (status, note.strip() if isinstance(note, str) else None,
                 session["admin_id"], status, request_id),
            ).fetchone()
            if not row:
                return jsonify({"error": "request_not_reviewable"}), 409
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,student_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,%s,'admin.data_rights.reviewed','data_rights_request',%s,%s)""",
                (session["admin_id"], row["student_id"], request_id,
                 Jsonb({"request_type": row["request_type"], "status": status})),
            )
        return jsonify({"request_id": str(row["id"]), "status": row["status"]}), 200
    except Exception:
        current_app.logger.exception("Admin data-rights review failed")
        return jsonify({"error": "admin_data_rights_review_failed"}), 503
