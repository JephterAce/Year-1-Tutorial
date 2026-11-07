"""Role-gated assessment authoring and publication for administrators.

Published assessments are immutable at the database layer. A revision is a new
assessment record; answer keys are never returned by these admin read routes.
"""
import math
from decimal import Decimal, InvalidOperation
from uuid import UUID

from flask import Blueprint, current_app, jsonify, request
from psycopg.types.json import Jsonb

from database import connection
from admin_policy import require

admin_assessments = Blueprint("admin_assessments", __name__)
QUESTION_TYPES = {"single_choice", "multiple_select", "true_false", "numeric", "exact_text"}


class AssessmentInputError(ValueError):
    pass


def _session():
    from admin_auth import authenticate_admin
    return authenticate_admin(request.cookies.get("learnwise_admin_session"))


def _authorise(capability, csrf=False):
    from admin_auth import validate_admin_csrf
    session = _session()
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
        raise AssessmentInputError("invalid_id")


def _question_payload(data):
    if not isinstance(data, dict):
        raise AssessmentInputError("question_object_required")
    kind = data.get("question_type")
    if kind not in QUESTION_TYPES:
        raise AssessmentInputError("unsupported_question_type")
    prompt = data.get("prompt")
    if not isinstance(prompt, (str, dict)) or not prompt:
        raise AssessmentInputError("question_prompt_required")
    if isinstance(prompt, str) and not 5 <= len(prompt.strip()) <= 4000:
        raise AssessmentInputError("question_prompt_length_invalid")
    if isinstance(prompt, dict) and not prompt:
        raise AssessmentInputError("question_prompt_required")
    options = data.get("options")
    option_ids = set()
    if kind in {"single_choice", "multiple_select"}:
        if not isinstance(options, list) or not 2 <= len(options) <= 10:
            raise AssessmentInputError("question_options_required")
        for option in options:
            if not isinstance(option, dict):
                raise AssessmentInputError("invalid_question_option")
            oid, label = option.get("id"), option.get("text")
            if not isinstance(oid, str) or not oid.strip() or not isinstance(label, str) or not label.strip():
                raise AssessmentInputError("invalid_question_option")
            if oid in option_ids:
                raise AssessmentInputError("duplicate_question_option")
            option_ids.add(oid)
    elif options is not None and not isinstance(options, list):
        raise AssessmentInputError("invalid_question_options")
    answer_key = data.get("answer_key")
    if not isinstance(answer_key, dict):
        raise AssessmentInputError("answer_key_required")
    accepted = None
    tolerance = None
    if kind == "single_choice":
        if answer_key.get("correct_option_id") not in option_ids:
            raise AssessmentInputError("correct_option_must_match_option")
    elif kind == "multiple_select":
        ids = answer_key.get("correct_option_ids")
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or not set(ids) <= option_ids:
            raise AssessmentInputError("correct_options_must_match_options")
    elif kind == "true_false":
        if not isinstance(answer_key.get("correct"), bool):
            raise AssessmentInputError("true_false_answer_required")
    elif kind == "numeric":
        try:
            value = Decimal(str(answer_key.get("value")))
            tolerance = Decimal(str(data.get("numeric_tolerance", 0)))
            if not value.is_finite() or not tolerance.is_finite() or tolerance < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError, TypeError):
            raise AssessmentInputError("numeric_answer_or_tolerance_invalid")
    elif kind == "exact_text":
        accepted = data.get("accepted_answers")
        if not isinstance(accepted, list) or not accepted or len(accepted) > 30 or not all(isinstance(x, str) and x.strip() for x in accepted):
            raise AssessmentInputError("accepted_text_answers_required")
    try:
        points = Decimal(str(data.get("points", 1)))
        if not points.is_finite() or points <= 0 or points > 1000:
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        raise AssessmentInputError("question_points_invalid")
    explanation = data.get("explanation")
    if explanation is not None and (not isinstance(explanation, str) or len(explanation) > 4000):
        raise AssessmentInputError("question_explanation_invalid")
    return {
        "question_type": kind, "prompt": prompt, "options": options,
        "answer_key": answer_key, "accepted_answers": accepted,
        "numeric_tolerance": tolerance, "points": points,
        "explanation": explanation, "sort_order": data.get("sort_order", 0),
    }


@admin_assessments.get("/api/v1/admin/assessments")
def list_assessments():
    session, error = _authorise("assessment.read")
    if error:
        return error
    try:
        with connection() as conn:
            rows = conn.execute(
                """SELECT a.id,a.title,a.description,a.class_level,a.status,a.version,
                          a.pass_mark_percent,a.max_attempts,a.available_from,a.available_until,
                          s.name AS subject,count(q.id) FILTER (WHERE q.is_active) AS question_count,
                          a.created_at,a.updated_at
                   FROM assessments a JOIN subjects s ON s.id=a.subject_id
                   LEFT JOIN assessment_questions q ON q.assessment_id=a.id
                   GROUP BY a.id,s.name ORDER BY a.updated_at DESC LIMIT 200"""
            ).fetchall()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.assessments.viewed','assessments','list-view',%s)""",
                (session["admin_id"], Jsonb({"returned_count": len(rows)})),
            )
        return jsonify({"items": [{
            "id": str(r["id"]), "title": r["title"], "description": r["description"],
            "class_level": r["class_level"], "subject": r["subject"], "status": r["status"],
            "version": r["version"], "pass_mark_percent": float(r["pass_mark_percent"]),
            "max_attempts": r["max_attempts"], "question_count": r["question_count"],
            "available_from": r["available_from"].isoformat() if r["available_from"] else None,
            "available_until": r["available_until"].isoformat() if r["available_until"] else None,
            "created_at": r["created_at"].isoformat(), "updated_at": r["updated_at"].isoformat(),
        } for r in rows]}), 200
    except Exception:
        current_app.logger.exception("Admin assessment list failed")
        return jsonify({"error": "admin_assessments_unavailable"}), 503


@admin_assessments.get("/api/v1/admin/assessments/<assessment_id>")
def get_assessment(assessment_id):
    session, error = _authorise("assessment.read")
    if error:
        return error
    try:
        assessment_id = _uuid(assessment_id)
    except AssessmentInputError:
        return jsonify({"error": "invalid_assessment_id"}), 400
    try:
        with connection() as conn:
            assessment = conn.execute(
                """SELECT a.id,a.title,a.description,a.class_level,a.status,a.version,
                          a.pass_mark_percent,a.max_attempts,a.allowed_question_counts,
                          a.available_from,a.available_until,s.name AS subject
                   FROM assessments a JOIN subjects s ON s.id=a.subject_id WHERE a.id=%s""",
                (assessment_id,),
            ).fetchone()
            if not assessment:
                return jsonify({"error": "assessment_not_found"}), 404
            questions = conn.execute(
                """SELECT id,question_type,prompt,options,explanation,points,sort_order
                   FROM assessment_questions WHERE assessment_id=%s AND is_active=true
                   ORDER BY sort_order,id""", (assessment_id,)
            ).fetchall()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.assessment.viewed','assessment',%s,%s)""",
                (session["admin_id"], assessment_id, Jsonb({"question_count": len(questions)})),
            )
        return jsonify({
            "assessment": {
                "id": str(assessment["id"]), "title": assessment["title"],
                "description": assessment["description"], "class_level": assessment["class_level"],
                "status": assessment["status"], "version": assessment["version"],
                "subject": assessment["subject"], "pass_mark_percent": float(assessment["pass_mark_percent"]),
                "max_attempts": assessment["max_attempts"],
                "allowed_question_counts": assessment["allowed_question_counts"],
                "available_from": assessment["available_from"].isoformat() if assessment["available_from"] else None,
                "available_until": assessment["available_until"].isoformat() if assessment["available_until"] else None,
            },
            "questions": [{
                "id": str(q["id"]), "question_type": q["question_type"],
                "prompt": q["prompt"], "options": q["options"],
                "explanation": q["explanation"], "points": float(q["points"]),
                "sort_order": q["sort_order"],
            } for q in questions],
        }), 200
    except Exception:
        current_app.logger.exception("Admin assessment detail failed")
        return jsonify({"error": "admin_assessment_unavailable"}), 503


@admin_assessments.post("/api/v1/admin/assessments")
def create_assessment():
    session, error = _authorise("assessment.edit", csrf=True)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    title, class_level = data.get("title"), data.get("class_level")
    if not isinstance(title, str) or not 3 <= len(title.strip()) <= 180:
        return jsonify({"error": "assessment_title_invalid"}), 400
    if class_level not in {"SS1", "SS2", "SS3"}:
        return jsonify({"error": "invalid_class_level"}), 400
    try:
        subject_id = _uuid(data.get("subject_id"))
        pass_mark = Decimal(str(data.get("pass_mark_percent", 50)))
        max_attempts = data.get("max_attempts", 1)
        allowed = data.get("allowed_question_counts", [5, 10, 20])
        if not pass_mark.is_finite() or not 0 <= pass_mark <= 100:
            raise InvalidOperation
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= 10:
            raise InvalidOperation
        if not isinstance(allowed, list) or not allowed or any(isinstance(x, bool) or not isinstance(x, int) or not 1 <= x <= 100 for x in allowed) or len(set(allowed)) != len(allowed):
            raise InvalidOperation
    except (AssessmentInputError, InvalidOperation, ValueError, TypeError):
        return jsonify({"error": "assessment_configuration_invalid"}), 400
    description = data.get("description")
    if description is not None and (not isinstance(description, str) or len(description) > 2000):
        return jsonify({"error": "assessment_description_invalid"}), 400
    try:
        with connection() as conn:
            subject = conn.execute("SELECT id FROM subjects WHERE id=%s", (subject_id,)).fetchone()
            if not subject:
                return jsonify({"error": "subject_not_found"}), 404
            row = conn.execute(
                """INSERT INTO assessments(subject_id,class_level,title,description,status,
                       pass_mark_percent,max_attempts,allowed_question_counts)
                   VALUES (%s,%s,%s,%s,'draft',%s,%s,%s) RETURNING id,title,status,version""",
                (subject_id, class_level, title.strip(), description, pass_mark, max_attempts, allowed),
            ).fetchone()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.assessment.created','assessment',%s,%s)""",
                (session["admin_id"], str(row["id"]), Jsonb({"class_level": class_level})),
            )
        return jsonify({"assessment_id": str(row["id"]), "title": row["title"],
                        "status": row["status"], "version": row["version"]}), 201
    except Exception:
        current_app.logger.exception("Admin assessment creation failed")
        return jsonify({"error": "admin_assessment_create_failed"}), 503


@admin_assessments.post("/api/v1/admin/assessments/<assessment_id>/questions")
def add_assessment_question(assessment_id):
    session, error = _authorise("assessment.edit", csrf=True)
    if error:
        return error
    try:
        assessment_id = _uuid(assessment_id)
        payload = _question_payload(request.get_json(silent=True) or {})
    except AssessmentInputError as exc:
        return jsonify({"error": str(exc)}), 400
    try:
        sort_order = payload["sort_order"]
        if isinstance(sort_order, bool) or not isinstance(sort_order, int) or not 0 <= sort_order <= 1000:
            return jsonify({"error": "question_order_invalid"}), 400
        with connection() as conn:
            parent = conn.execute(
                "SELECT status FROM assessments WHERE id=%s FOR UPDATE", (assessment_id,)
            ).fetchone()
            if not parent:
                return jsonify({"error": "assessment_not_found"}), 404
            if parent["status"] != "draft":
                return jsonify({"error": "published_assessment_is_immutable"}), 409
            row = conn.execute(
                """INSERT INTO assessment_questions
                   (assessment_id,question_type,prompt,options,answer_key,explanation,points,
                    numeric_tolerance,accepted_answers,sort_order)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (assessment_id,payload["question_type"],Jsonb(payload["prompt"]),
                 Jsonb(payload["options"]) if payload["options"] is not None else None,
                 Jsonb(payload["answer_key"]),payload["explanation"],payload["points"],
                 payload["numeric_tolerance"],Jsonb(payload["accepted_answers"]) if payload["accepted_answers"] is not None else None,
                 sort_order),
            ).fetchone()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.assessment.question_added','assessment_question',%s,%s)""",
                (session["admin_id"], str(row["id"]), Jsonb({"assessment_id": assessment_id, "question_type": payload["question_type"]})),
            )
        return jsonify({"question_id": str(row["id"]), "assessment_id": assessment_id}), 201
    except Exception:
        current_app.logger.exception("Admin assessment question creation failed")
        return jsonify({"error": "admin_assessment_question_create_failed"}), 503


@admin_assessments.post("/api/v1/admin/assessments/<assessment_id>/publish")
def publish_assessment(assessment_id):
    session, error = _authorise("assessment.publish", csrf=True)
    if error:
        return error
    try:
        assessment_id = _uuid(assessment_id)
    except AssessmentInputError:
        return jsonify({"error": "invalid_assessment_id"}), 400
    try:
        with connection() as conn:
            parent = conn.execute(
                """SELECT id,allowed_question_counts FROM assessments
                   WHERE id=%s AND status='draft' FOR UPDATE""", (assessment_id,)
            ).fetchone()
            if not parent:
                return jsonify({"error": "draft_assessment_not_found"}), 409
            counts = conn.execute(
                """SELECT count(*) AS total,COALESCE(sum(points),0) AS maximum
                   FROM assessment_questions WHERE assessment_id=%s AND is_active=true""",
                (assessment_id,),
            ).fetchone()
            total = int(counts["total"])
            if total < 1 or total > 100 or any(int(n) > total for n in parent["allowed_question_counts"]):
                return jsonify({"error": "assessment_question_count_invalid"}), 409
            if Decimal(str(counts["maximum"])) <= 0:
                return jsonify({"error": "assessment_total_points_invalid"}), 409
            row = conn.execute(
                """UPDATE assessments SET status='published',updated_at=now()
                   WHERE id=%s AND status='draft' RETURNING id,status,version""",
                (assessment_id,),
            ).fetchone()
            conn.execute(
                """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
                   VALUES (%s,'admin.assessment.published','assessment',%s,%s)""",
                (session["admin_id"], assessment_id, Jsonb({"question_count": total})),
            )
        return jsonify({"assessment_id": str(row["id"]), "status": row["status"],
                        "version": row["version"], "question_count": total}), 200
    except Exception:
        current_app.logger.exception("Admin assessment publish failed")
        return jsonify({"error": "admin_assessment_publish_failed"}), 503
