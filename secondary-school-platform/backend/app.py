"""Isolated Flask API for the senior-secondary learning platform.

Without DATABASE_URL this serves clearly-labelled demo catalogue data.
With DATABASE_URL it enables the database-backed student, assessment,
admin-review, payment-webhook and protected-media routes. Provider credentials
and production infrastructure remain explicit deployment prerequisites.
"""
import os
from decimal import Decimal
from uuid import UUID

from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context, redirect

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024


def _secure_cookie():
    """Require Secure cookies in staging and production deployments."""
    return os.environ.get("APP_ENV", "development").strip().lower() in {"staging", "production"}

DEMO_CATALOGUE = [
    {"subject": "English Language", "title": "Reading comprehension and inference", "term": "Term allocation pending", "demo": True},
    {"subject": "General Mathematics", "title": "Quadratic equations", "term": "Term allocation pending", "demo": True},
    {"subject": "Biology", "title": "Cell structure and organisation", "term": "Term allocation pending", "demo": True},
    {"subject": "Chemistry", "title": "Atomic structure", "term": "Term allocation pending", "demo": True},
    {"subject": "Physics", "title": "Motion and linear kinematics", "term": "Term allocation pending", "demo": True},
    {"subject": "Further Mathematics", "title": "Functions and mappings", "term": "Term allocation pending", "demo": True},
]


def serialise_topic(row):
    result = dict(row)
    for key, value in result.items():
        if isinstance(value, (UUID, Decimal)):
            result[key] = str(value) if isinstance(value, UUID) else int(value)
    return result


@app.get("/health")
def health():
    if not os.environ.get("DATABASE_URL"):
        return jsonify({"status": "ok", "service": "secondary-school-api", "mode": "demo"})
    from database import database_ready
    if not database_ready():
        return jsonify({"status": "degraded", "service": "secondary-school-api", "database": "unavailable"}), 503
    return jsonify({"status": "ok", "service": "secondary-school-api", "mode": "database"})


@app.get("/api/v1/catalogue")
def catalogue():
    class_level = request.args.get("class")
    subject_slug = request.args.get("subject")
    term_raw = request.args.get("term")
    search = request.args.get("q", "").strip()[:100] or None

    if class_level and class_level not in ("SS1", "SS2", "SS3"):
        return jsonify({"error": "invalid_class", "message": "Class must be SS1, SS2 or SS3."}), 400
    term_number = None
    if term_raw:
        try:
            term_number = int(term_raw)
        except ValueError:
            return jsonify({"error": "invalid_term", "message": "Term must be 1, 2 or 3."}), 400
        if term_number not in (1, 2, 3):
            return jsonify({"error": "invalid_term", "message": "Term must be 1, 2 or 3."}), 400

    if not os.environ.get("DATABASE_URL"):
        items = DEMO_CATALOGUE
        # Demo topics are deliberately not assigned to a class; class mapping requires curriculum verification.
        if subject_slug:
            items = [x for x in items if x["subject"].lower().replace(" ", "-") == subject_slug]
        if search:
            items = [x for x in items if search.lower() in (x["title"] + " " + x["subject"]).lower()]
        return jsonify({
            "items": items,
            "is_demo": True,
            "notice": "Illustrative sample data; not a verified curriculum or published lesson catalogue.",
        })

    try:
        from database import list_published_topics
        rows = list_published_topics(class_level, subject_slug, term_number, search)
        return jsonify({"items": [serialise_topic(row) for row in rows], "is_demo": False})
    except Exception:
        app.logger.exception("Catalogue query failed")
        return jsonify({"error": "catalogue_unavailable", "message": "The catalogue is temporarily unavailable."}), 503


@app.post("/api/v1/webhooks/paystack")
def paystack_webhook():
    """Public provider callback; authenticates raw body and verifies transaction."""
    from paystack_webhooks import PaystackWebhookError
    from payments import PaymentProcessingError, process_paystack_charge_success

    signature = request.headers.get("x-paystack-signature", "")
    raw_body = request.get_data(cache=False, as_text=False)
    try:
        result = process_paystack_charge_success(raw_body, signature)
        return jsonify({"received": True, "payment": result}), 200
    except PaystackWebhookError:
        return jsonify({"error": "invalid_webhook"}), 400
    except PaymentProcessingError:
        app.logger.exception("Paystack payment could not be safely fulfilled")
        return jsonify({"error": "payment_processing_unavailable"}), 503
    except Exception:
        app.logger.exception("Unexpected Paystack webhook failure")
        return jsonify({"error": "webhook_unavailable"}), 503


@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    if _secure_cookie():
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "not_found", "message": "The requested resource was not found."}), 404



def _feature_enabled(name):
    value = os.environ.get(name)
    if value is not None:
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return os.environ.get("APP_ENV", "development").strip().lower() not in {"staging", "production"}

@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "internal_error", "message": "An unexpected error occurred."}), 500



@app.post("/api/v1/auth/register")
def register():
    if not _feature_enabled("STUDENT_REGISTRATION_ENABLED"):
        return jsonify({"error":"registration_temporarily_disabled"}),503
    from identity_service import register_student, IdentityError
    from identity_email import send_identity_link
    data = request.get_json(silent=True) or {}
    if data.get("accept_terms") is not True or data.get("accept_privacy") is not True:
        return jsonify({"error": "consent_required"}), 400
    try:
        result = register_student(
            data.get("email"), data.get("username"), data.get("display_name"),
            data.get("class_level"), data.get("password"),
        )
        send_identity_link(result["student"]["email"], result["verification_token"], "verify")
        return jsonify({"message": "If the details are eligible, a verification email will be sent."}), 202
    except (ValueError, IdentityError) as exc:
        return jsonify({"error": "registration_unavailable", "message": str(exc)}), 400
    except Exception:
        app.logger.exception("Student registration failed")
        return jsonify({"error": "registration_unavailable"}), 503


@app.post("/api/v1/auth/verify-email")
def verify_email():
    from identity_service import verify_student_email, IdentityError
    data = request.get_json(silent=True) or {}
    try:
        verify_student_email(data.get("token"))
        return jsonify({"verified": True}), 200
    except IdentityError:
        return jsonify({"error": "invalid_or_expired_link"}), 400
    except Exception:
        app.logger.exception("Email verification failed")
        return jsonify({"error": "verification_unavailable"}), 503


@app.post("/api/v1/auth/login")
def login():
    from identity_service import login_student, IdentityError
    data = request.get_json(silent=True) or {}
    try:
        result = login_student(data.get("email"), data.get("password"))
        response = jsonify({"authenticated": True})
        secure = _secure_cookie()
        response.set_cookie(
            "learnwise_session", result["session_id"], httponly=True, secure=secure,
            samesite="Lax", path="/", max_age=12 * 60 * 60,
        )
        response.set_cookie(
            "learnwise_csrf", result["csrf_token"], httponly=False, secure=secure,
            samesite="Lax", path="/", max_age=12 * 60 * 60,
        )
        return response
    except IdentityError:
        return jsonify({"error": "invalid_credentials_or_unverified"}), 401
    except Exception:
        app.logger.exception("Student login failed")
        return jsonify({"error": "login_unavailable"}), 503


def _current_student(require_csrf=False):
    from identity_service import authenticate_session, validate_csrf
    session = authenticate_session(request.cookies.get("learnwise_session"))
    if not session:
        return None
    if require_csrf and not validate_csrf(session, request.headers.get("X-CSRF-Token", "")):
        return None
    return session


@app.get("/api/v1/auth/me")
def current_student():
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    student.pop("csrf_token_hash", None)
    student.pop("session_row_id", None)
    student["id"] = str(student.pop("student_id"))
    return jsonify({"student": student})


@app.post("/api/v1/auth/logout")
def logout():
    from identity_service import logout_student
    if not _current_student(require_csrf=True):
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    logout_student(request.cookies.get("learnwise_session"))
    response = jsonify({"logged_out": True})
    response.delete_cookie("learnwise_session", path="/", samesite="Lax")
    response.delete_cookie("learnwise_csrf", path="/", samesite="Lax")
    return response


@app.post("/api/v1/auth/password-reset")
def password_reset_request():
    from identity_service import request_password_reset
    from identity_email import send_identity_link
    data = request.get_json(silent=True) or {}
    try:
        token = request_password_reset(data.get("email"))
        if token:
            # The database returns the associated address only after a matching active account.
            from database import connection
            import hashlib
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            with connection() as conn:
                row = conn.execute(
                    """SELECT s.email FROM identity_tokens t JOIN students s ON s.id=t.student_id
                       WHERE t.token_hash=%s AND t.purpose='reset_student_password'""",
                    (digest,),
                ).fetchone()
            if row:
                send_identity_link(row["email"], token, "reset")
        return jsonify({"message": "If an eligible account exists, reset instructions will be sent."}), 202
    except Exception:
        app.logger.exception("Password reset request could not be processed")
        return jsonify({"message": "If an eligible account exists, reset instructions will be sent."}), 202


@app.post("/api/v1/auth/password-reset/complete")
def password_reset_complete():
    from identity_service import reset_student_password, IdentityError
    data = request.get_json(silent=True) or {}
    try:
        reset_student_password(data.get("token"), data.get("new_password"))
        return jsonify({"password_reset": True}), 200
    except (IdentityError, ValueError):
        return jsonify({"error": "invalid_or_expired_link_or_password"}), 400
    except Exception:
        app.logger.exception("Password reset failed")
        return jsonify({"error": "password_reset_unavailable"}), 503


# Assessment execution endpoints. All require a verified student session and CSRF.
def _assessment_student():
    student = _current_student(require_csrf=True)
    return student


@app.post("/api/v1/assessments/<assessment_id>/attempts")
def create_assessment_attempt(assessment_id):
    from assessment_attempts import create_attempt, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        result = create_attempt(student["student_id"], assessment_id, data.get("question_count"))
        return jsonify(result), 201
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment attempt creation failed")
        return jsonify({"error": "assessment_unavailable"}), 503


@app.post("/api/v1/assessment-attempts/<attempt_id>/start")
def start_assessment_attempt(attempt_id):
    from assessment_attempts import start_attempt, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(start_attempt(student["student_id"], attempt_id,
                                     data.get("accepted"), data.get("policy_version"))), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment attempt start failed")
        return jsonify({"error": "assessment_start_unavailable"}), 503


@app.get("/api/v1/assessment-attempts/<attempt_id>")
def get_assessment_attempt(attempt_id):
    from assessment_attempts import get_attempt, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    try:
        return jsonify(get_attempt(student["student_id"], attempt_id)), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment attempt fetch failed")
        return jsonify({"error": "assessment_unavailable"}), 503


@app.put("/api/v1/assessment-attempts/<attempt_id>/answers/<question_id>")
def save_assessment_answer(attempt_id, question_id):
    from assessment_attempts import save_answer, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    if "answer" not in data:
        return jsonify({"error": "answer_required"}), 400
    try:
        return jsonify(save_answer(student["student_id"], attempt_id, question_id, data["answer"])), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment answer save failed")
        return jsonify({"error": "answer_save_unavailable"}), 503


@app.post("/api/v1/assessment-attempts/<attempt_id>/submit")
def submit_assessment_attempt(attempt_id):
    from assessment_attempts import submit_attempt, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    try:
        return jsonify(submit_attempt(student["student_id"], attempt_id)), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment submission failed")
        return jsonify({"error": "submission_unavailable"}), 503


@app.post("/api/v1/assessment-attempts/<attempt_id>/integrity-events")
def assessment_integrity_event(attempt_id):
    from assessment_attempts import record_integrity_event, AttemptError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(record_integrity_event(student["student_id"], attempt_id,
                                              data.get("event_type"))), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment integrity event failed")
        return jsonify({"error": "integrity_event_unavailable"}), 503


@app.post("/api/v1/topics/<topic_id>/checkout")
def create_topic_checkout(topic_id):
    if not _feature_enabled("PAYMENTS_ENABLED"):
        return jsonify({"error":"payments_temporarily_disabled"}),503
    from payment_orders import create_topic_checkout, PaymentOrderError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        result = create_topic_checkout(student["student_id"], topic_id)
        return jsonify(result), 201
    except PaymentOrderError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Topic checkout initialisation failed")
        return jsonify({"error": "checkout_unavailable"}), 503


@app.post("/api/v1/tutor/answer")
def answer_tutor_question():
    """Authenticated, CSRF-protected AI tutoring; disabled until explicitly configured."""
    if os.environ.get("AI_TUTOR_ENABLED", "").strip().lower() not in {"1", "true", "yes", "on"}:
        return jsonify({"error": "ai_tutor_temporarily_disabled"}), 503
    student = _current_student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401

    data = request.get_json(silent=True) or {}
    try:
        from ai_tutor import (
            generate_tutor_answer, build_tutor_messages,
            TutorConfigurationError, TutorProviderError
        )
        from ai_tutor_quota import reserve_tutor_usage, TutorQuotaError
        messages = build_tutor_messages(
            student.get("class_level"), data.get("question"), data.get("topic_context")
        )
        bounded_prompt = "\\n".join(item["content"] for item in messages)
        reserve_tutor_usage(student["student_id"], bounded_prompt)
        answer = generate_tutor_answer(
            student.get("class_level"),
            data.get("question"),
            data.get("topic_context"),
        )
        return jsonify({"answer": answer}), 200
    except TutorQuotaError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except ValueError as exc:
        return jsonify({"error": "invalid_tutor_request", "message": str(exc)}), 400
    except TutorConfigurationError:
        app.logger.warning("AI tutor is enabled but provider configuration is incomplete or invalid")
        return jsonify({"error": "ai_tutor_unavailable"}), 503
    except TutorProviderError:
        app.logger.warning("AI tutor provider request failed")
        return jsonify({"error": "ai_tutor_unavailable"}), 503
    except Exception:
        app.logger.exception("AI tutor request failed unexpectedly")
        return jsonify({"error": "ai_tutor_unavailable"}), 503


@app.get("/api/v1/topics/<topic_id>/lesson-content")
def read_lesson_content(topic_id):
    from lesson_content import get_lesson_content, LessonContentError
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        return jsonify(get_lesson_content(student["student_id"], topic_id)), 200
    except LessonContentError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Lesson content fetch failed")
        return jsonify({"error": "lesson_content_unavailable"}), 503


@app.post("/api/v1/topics/<topic_id>/practice/<question_id>")
def answer_lesson_practice(topic_id, question_id):
    from lesson_content import check_practice_answer, LessonContentError
    student = _current_student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    if "answer" not in data:
        return jsonify({"error": "answer_required"}), 400
    try:
        return jsonify(check_practice_answer(
            student["student_id"], topic_id, question_id, data["answer"]
        )), 200
    except LessonContentError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Lesson practice answer failed")
        return jsonify({"error": "practice_unavailable"}), 503


@app.post("/api/v1/topics/<topic_id>/progress/complete")
def complete_lesson_topic(topic_id):
    from lesson_content import mark_topic_complete, LessonContentError
    student = _current_student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    try:
        return jsonify(mark_topic_complete(student["student_id"], topic_id)), 200
    except LessonContentError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Lesson progress update failed")
        return jsonify({"error": "progress_unavailable"}), 503


@app.get("/api/v1/student/dashboard")
def student_dashboard():
    """Return authenticated, database-backed learning progress without invented metrics."""
    from database import connection
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        with connection() as conn:
            summary = conn.execute(
                """SELECT
                     (SELECT count(DISTINCT lp.topic_id)
                        FROM student_topic_progress lp
                        JOIN topics t ON t.id=lp.topic_id
                       WHERE lp.student_id=%s AND lp.completed_at IS NOT NULL
                         AND t.status='published' AND t.curriculum_status='published') AS completed_lessons,
                     (SELECT count(*) FROM assessment_attempts
                       WHERE student_id=%s AND status <> 'briefing') AS assessment_attempts,
                     (SELECT count(*) FROM assessment_attempts
                       WHERE student_id=%s AND passed IS TRUE) AS assessments_passed,
                     (SELECT round(avg(percentage),1) FROM assessment_attempts
                       WHERE student_id=%s AND percentage IS NOT NULL) AS average_score""",
                (student["student_id"], student["student_id"],
                 student["student_id"], student["student_id"]),
            ).fetchone()
            subjects = conn.execute(
                """SELECT s.slug,s.name,
                     count(DISTINCT t.id) AS published_lessons,
                     count(DISTINCT CASE WHEN lp.completed_at IS NOT NULL THEN t.id END) AS completed_lessons
                   FROM subjects s
                   LEFT JOIN topics t ON t.subject_id=s.id AND t.class_level=%s
                     AND t.status='published' AND t.curriculum_status='published'
                   LEFT JOIN student_topic_progress lp ON lp.topic_id=t.id
                     AND lp.student_id=%s AND lp.completed_at IS NOT NULL
                   WHERE s.is_active=true
                   GROUP BY s.id,s.slug,s.name,s.sort_order
                   ORDER BY s.sort_order,s.name""",
                (student["class_level"], student["student_id"]),
            ).fetchall()
            recent = conn.execute(
                """SELECT id,title,subject,updated_at FROM (
                     SELECT DISTINCT ON (t.id) t.id,t.title,s.name AS subject,lp.updated_at
                     FROM student_topic_progress lp
                     JOIN topics t ON t.id=lp.topic_id
                     JOIN subjects s ON s.id=t.subject_id
                     WHERE lp.student_id=%s AND t.status='published'
                       AND t.curriculum_status='published'
                     ORDER BY t.id,lp.updated_at DESC
                   ) recent_lessons
                   ORDER BY updated_at DESC LIMIT 8""",
                (student["student_id"],),
            ).fetchall()
        return jsonify({
            "student": {
                "display_name": student.get("display_name"),
                "class_level": student.get("class_level"),
            },
            "summary": {
                "completed_lessons": int(summary["completed_lessons"] or 0),
                "assessment_attempts": int(summary["assessment_attempts"] or 0),
                "assessments_passed": int(summary["assessments_passed"] or 0),
                "average_score": str(summary["average_score"]) if summary["average_score"] is not None else None,
            },
            "subjects": [{
                "slug": row["slug"], "name": row["name"],
                "published_lessons": int(row["published_lessons"]),
                "completed_lessons": int(row["completed_lessons"]),
            } for row in subjects],
            "recent_lessons": [{
                "id": str(row["id"]), "title": row["title"],
                "subject": row["subject"], "updated_at": row["updated_at"].isoformat(),
            } for row in recent],
            "source": "database",
        }), 200
    except Exception:
        app.logger.exception("Student dashboard query failed")
        return jsonify({"error": "dashboard_unavailable"}), 503


@app.get("/api/v1/student/profile")
def read_student_profile():
    from student_profiles import get_profile, ProfileError
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        return jsonify({"profile": get_profile(student["student_id"])}), 200
    except ProfileError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Student profile read failed")
        return jsonify({"error": "profile_unavailable"}), 503


@app.patch("/api/v1/student/profile")
def edit_student_profile():
    from student_profiles import update_profile, ProfileError
    student = _current_student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"profile": update_profile(student["student_id"], data)}), 200
    except ProfileError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Student profile update failed")
        return jsonify({"error": "profile_update_unavailable"}), 503


@app.get("/api/v1/assessments")
def list_student_assessments():
    from assessment_attempts import list_published_assessments, AttemptError
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        return jsonify({"items": list_published_assessments(student["student_id"])}), 200
    except AttemptError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Published assessment catalogue failed")
        return jsonify({"error": "assessment_catalogue_unavailable"}), 503


@app.post("/api/v1/assessment-attempts/<attempt_id>/reports")
def submit_assessment_issue_report(attempt_id):
    from assessment_reports import submit_assessment_report, AssessmentReportError
    student = _assessment_student()
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    try:
        result = submit_assessment_report(student["student_id"], attempt_id,
                                          request.get_json(silent=True) or {})
        return jsonify({"report": result}), 201
    except AssessmentReportError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment issue report submission failed")
        return jsonify({"error": "report_unavailable"}), 503


@app.get("/api/v1/assessment-attempts/<attempt_id>/reports")
def list_assessment_issue_reports(attempt_id):
    from assessment_reports import list_my_assessment_reports, AssessmentReportError
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        return jsonify({"items": list_my_assessment_reports(student["student_id"], attempt_id)}), 200
    except AssessmentReportError as exc:
        return jsonify({"error": exc.code, "message": str(exc)}), exc.status
    except Exception:
        app.logger.exception("Assessment issue report listing failed")
        return jsonify({"error": "report_list_unavailable"}), 503


# Dedicated admin identity routes. Account provisioning is deliberately offline-only.
@app.post("/api/v1/admin/auth/login")
def admin_login():
    from admin_auth import login_admin, AdminAuthError
    data = request.get_json(silent=True) or {}
    try:
        result = login_admin(data.get("email"), data.get("password"))
        response = jsonify({"authenticated": True})
        secure = _secure_cookie()
        response.set_cookie("learnwise_admin_session", result["session_id"], httponly=True,
                            secure=secure, samesite="Strict", path="/", max_age=8 * 60 * 60)
        response.set_cookie("learnwise_admin_csrf", result["csrf_token"], httponly=False,
                            secure=secure, samesite="Strict", path="/", max_age=8 * 60 * 60)
        return response
    except AdminAuthError:
        return jsonify({"error": "invalid_credentials"}), 401
    except Exception:
        app.logger.exception("Admin login failed")
        return jsonify({"error": "admin_auth_unavailable"}), 503


def _current_admin(require_csrf=False):
    from admin_auth import authenticate_admin, validate_admin_csrf
    session = authenticate_admin(request.cookies.get("learnwise_admin_session"))
    if not session:
        return None
    if require_csrf and not validate_admin_csrf(session, request.headers.get("X-CSRF-Token", "")):
        return None
    return session


@app.get("/api/v1/admin/auth/me")
def admin_me():
    session = _current_admin()
    if not session:
        return jsonify({"error": "unauthenticated"}), 401
    return jsonify({"admin": {"id": session["admin_id"], "email": session["email"],
                              "role": session["role"]}})


@app.post("/api/v1/admin/auth/logout")
def admin_logout():
    from admin_auth import logout_admin
    if not _current_admin(require_csrf=True):
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    logout_admin(request.cookies.get("learnwise_admin_session"))
    response = jsonify({"logged_out": True})
    response.delete_cookie("learnwise_admin_session", path="/", samesite="Strict")
    response.delete_cookie("learnwise_admin_csrf", path="/", samesite="Strict")
    return response


# Protected admin assessment review endpoints.
from admin_assessment_reviews import admin_reviews
app.register_blueprint(admin_reviews)
from admin_data import admin_data
app.register_blueprint(admin_data)


# Private lesson audio: signed access is scoped to an approved asset and active entitlement.
@app.post("/api/v1/topics/<topic_id>/audio/<asset_id>/access")
def create_private_audio_access(topic_id, asset_id):
    from audio_media import issue_audio_token, AudioAccessError
    from database import connection
    student = _current_student(require_csrf=True)
    if not student:
        return jsonify({"error": "unauthenticated_or_csrf_failed"}), 401
    try:
        with connection() as conn:
            row = conn.execute(
                """SELECT a.storage_key FROM lesson_assets a
                   JOIN topics t ON t.id=a.topic_id
                   WHERE a.id=%s AND a.topic_id=%s AND t.status='published'
                     AND a.review_status='approved'
                     AND a.asset_type IN ('teacher_audio','podcast_audio')
                     AND EXISTS (SELECT 1 FROM entitlements e
                                 WHERE e.student_id=%s AND e.topic_id=t.id
                                   AND e.revoked_at IS NULL)""",
                (asset_id, topic_id, student["student_id"]),
            ).fetchone()
        if not row:
            return jsonify({"error": "audio_not_available"}), 404
        token = issue_audio_token(
            str(student["student_id"]), str(topic_id), row["storage_key"], True, ttl=180
        )
        response = jsonify({"audio_url": f"/api/v1/private-audio/{topic_id}/{asset_id}"})
        secure = _secure_cookie()
        response.set_cookie(
            "learnwise_audio_access", token, httponly=True, secure=secure,
            samesite="Strict", path=f"/api/v1/private-audio/{topic_id}/{asset_id}",
            max_age=180,
        )
        return response, 200
    except AudioAccessError:
        return jsonify({"error": "audio_access_unavailable"}), 503
    except Exception:
        app.logger.exception("Private audio authorisation failed")
        return jsonify({"error": "audio_access_unavailable"}), 503


@app.get("/api/v1/private-audio/<topic_id>/<asset_id>")
def stream_private_audio(topic_id, asset_id):
    from audio_media import verify_audio_token, resolve_private_audio_path, AudioAccessError
    from database import connection
    from flask import send_file
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        token = request.cookies.get("learnwise_audio_access", "")
        claims = verify_audio_token(token)
        if claims.get("sub") != str(student["student_id"]) or claims.get("topic") != str(topic_id):
            return jsonify({"error": "audio_access_denied"}), 403
        with connection() as conn:
            row = conn.execute(
                """SELECT a.storage_key,a.mime_type FROM lesson_assets a
                   JOIN topics t ON t.id=a.topic_id
                   WHERE a.id=%s AND a.topic_id=%s AND t.status='published'
                     AND a.review_status='approved'
                     AND a.asset_type IN ('teacher_audio','podcast_audio')
                     AND EXISTS (SELECT 1 FROM entitlements e
                                 WHERE e.student_id=%s AND e.topic_id=t.id
                                   AND e.revoked_at IS NULL)""",
                (asset_id, topic_id, student["student_id"]),
            ).fetchone()
        if not row or claims.get("key") != row["storage_key"]:
            return jsonify({"error": "audio_access_denied"}), 403
        if os.environ.get("AUDIO_STORAGE_BACKEND", "local").strip().lower() == "neon_s3":
            from audio_storage import get_private_audio_object
            stored = get_private_audio_object(row["storage_key"], request.headers.get("Range"))
            body = stored["Body"]
            response = Response(
                stream_with_context(body.iter_chunks(chunk_size=64 * 1024)),
                status=206 if request.headers.get("Range") else 200,
                mimetype=stored.get("ContentType") or row["mime_type"] or "application/octet-stream",
            )
            response.headers["Content-Length"] = str(stored["ContentLength"])
            if stored.get("ContentRange"):
                response.headers["Content-Range"] = stored["ContentRange"]
            response.headers["Accept-Ranges"] = "bytes"
        else:
            media_path = resolve_private_audio_path(
                os.environ.get("AUDIO_STORAGE_ROOT", ""), row["storage_key"]
            )
            response = send_file(
                media_path, mimetype=row["mime_type"] or "application/octet-stream",
                conditional=True, etag=True, max_age=0,
            )
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response
    except AudioAccessError:
        return jsonify({"error": "audio_unavailable"}), 404
    except Exception:
        app.logger.exception("Private audio stream failed")
        return jsonify({"error": "audio_unavailable"}), 503


@app.get("/api/v1/topics/<topic_id>")
def get_student_topic(topic_id):
    from database import connection
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        with connection() as conn:
            topic = conn.execute(
                """SELECT t.id,t.class_level,t.title,t.summary,t.learning_objectives,
                          t.price_kobo,t.currency,s.name AS subject
                   FROM topics t JOIN subjects s ON s.id=t.subject_id
                   JOIN curriculum_versions cv ON cv.id=t.curriculum_version_id
                   JOIN curriculum_source_records csr ON csr.id=t.curriculum_source_record_id
                   WHERE t.id=%s AND t.status='published' AND t.curriculum_status='published'
                     AND cv.version_code='nerdc_ssec_2025'
                     AND csr.verification_status='approved'""",
                (topic_id,),
            ).fetchone()
            if not topic:
                return jsonify({"error": "topic_not_found"}), 404
            entitlement = conn.execute(
                """SELECT 1 FROM entitlements WHERE student_id=%s AND topic_id=%s
                   AND revoked_at IS NULL LIMIT 1""",
                (student["student_id"], topic_id),
            ).fetchone()
            assets = []
            if entitlement:
                assets = conn.execute(
                    """SELECT id,asset_type,duration_seconds,mime_type
                       FROM lesson_assets WHERE topic_id=%s AND review_status='approved'
                         AND asset_type IN ('teacher_audio','podcast_audio','transcript','notes')
                       ORDER BY asset_type,version DESC""",
                    (topic_id,),
                ).fetchall()
        result = {key: (str(value) if key == "id" else value)
                  for key, value in topic.items()}
        result["has_access"] = bool(entitlement)
        result["assets"] = [
            {"id": str(a["id"]), "asset_type": a["asset_type"],
             "duration_seconds": a["duration_seconds"], "mime_type": a["mime_type"]}
            for a in assets
        ]
        return jsonify({"topic": result}), 200
    except Exception:
        app.logger.exception("Student topic detail failed")
        return jsonify({"error": "topic_unavailable"}), 503


@app.get("/api/v1/student/assessment-history")
def student_assessment_history():
    from database import connection
    student = _current_student()
    if not student:
        return jsonify({"error": "unauthenticated"}), 401
    try:
        with connection() as conn:
            rows = conn.execute(
                """SELECT a.id,a.title,s.name AS subject,a.class_level,
                          x.status,x.question_count,x.score,x.maximum_score,x.percentage,
                          x.passed,x.integrity_review_required,x.started_at,x.submitted_at
                   FROM assessment_attempts x
                   JOIN assessments a ON a.id=x.assessment_id
                   JOIN subjects s ON s.id=a.subject_id
                   WHERE x.student_id=%s AND x.status <> 'briefing'
                   ORDER BY x.created_at DESC LIMIT 100""",
                (student["student_id"],),
            ).fetchall()
        return jsonify({"items": [
            {"attempt_id": str(row["id"]), "title": row["title"], "subject": row["subject"],
             "class_level": row["class_level"], "status": row["status"],
             "question_count": row["question_count"],
             "score": str(row["score"]) if row["score"] is not None else None,
             "maximum_score": str(row["maximum_score"]) if row["maximum_score"] is not None else None,
             "percentage": str(row["percentage"]) if row["percentage"] is not None else None,
             "passed": row["passed"], "integrity_review_required": row["integrity_review_required"],
             "started_at": row["started_at"].isoformat() if row["started_at"] else None,
             "submitted_at": row["submitted_at"].isoformat() if row["submitted_at"] else None}
            for row in rows
        ]}), 200
    except Exception:
        app.logger.exception("Student assessment history failed")
        return jsonify({"error": "assessment_history_unavailable"}), 503



# Same-origin student and administrator web pages.
# Static assets are copied into the container by backend/Dockerfile.
_BACKEND_DIR = os.path.dirname(__file__)
_PROJECT_DIR = _BACKEND_DIR if os.path.isdir(os.path.join(_BACKEND_DIR, "frontend")) else os.path.dirname(_BACKEND_DIR)
_FRONTEND_DIR = os.path.join(_PROJECT_DIR, "frontend")
_ADMIN_DIR = os.path.join(_PROJECT_DIR, "admin")

@app.get("/")
def student_home():
    return send_from_directory(_FRONTEND_DIR, "index.html")

@app.get("/account")
def student_account_page():
    return send_from_directory(_FRONTEND_DIR, "account.html")

@app.get("/assessment")
def student_assessment_page():
    return send_from_directory(_FRONTEND_DIR, "assessment.html")

@app.get("/lesson")
def student_lesson_page():
    return send_from_directory(_FRONTEND_DIR, "lesson.html")


@app.get("/index.html")
def student_home_alias():
    return send_from_directory(_FRONTEND_DIR, "index.html")

@app.get("/account.html")
def student_account_alias():
    return send_from_directory(_FRONTEND_DIR, "account.html")

@app.get("/assessment.html")
def student_assessment_alias():
    return send_from_directory(_FRONTEND_DIR, "assessment.html")

@app.get("/lesson.html")
def student_lesson_alias():
    return send_from_directory(_FRONTEND_DIR, "lesson.html")

@app.get("/learnwise-ui.css")
def student_stylesheet():
    return send_from_directory(_FRONTEND_DIR, "learnwise-ui.css", mimetype="text/css")

@app.get("/assets/<path:filename>")
def student_assets(filename):
    return send_from_directory(_FRONTEND_DIR, filename)

@app.get("/admin/login")
def admin_login_page():
    if _current_admin():
        return redirect("/admin")
    response = send_from_directory(_ADMIN_DIR, "login.html")
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/admin")
def admin_workspace_page():
    if not _current_admin():
        return redirect("/admin/login")
    response = send_from_directory(_ADMIN_DIR, "index.html")
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/admin/operations")
def admin_operations_page():
    if not _current_admin():
        return redirect("/admin/login")
    response = send_from_directory(_ADMIN_DIR, "operations.html")
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/admin/reviews")
def admin_reviews_page():
    if not _current_admin():
        return redirect("/admin/login")
    response = send_from_directory(_ADMIN_DIR, "reviews.html")
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    # Local development only. Use a production WSGI server in deployment.
    app.run(host="127.0.0.1", port=8000, debug=False)
