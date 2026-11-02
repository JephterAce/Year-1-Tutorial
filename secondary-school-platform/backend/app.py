"""Isolated Flask API for the senior-secondary learning platform.

Without DATABASE_URL this serves clearly-labelled demo catalogue data.
With DATABASE_URL it reads only published topics from the dedicated platform DB.
No payment, account or protected media endpoints are enabled yet.
"""
import os
from decimal import Decimal
from uuid import UUID

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

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


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "not_found", "message": "The requested resource was not found."}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "internal_error", "message": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    # Local development only. Use a production WSGI server in deployment.
    app.run(host="127.0.0.1", port=8000, debug=False)


@app.post("/api/v1/auth/register")
def register():
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
        secure = os.environ.get("APP_ENV", "development").lower() == "production"
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
