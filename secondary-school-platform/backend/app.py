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
