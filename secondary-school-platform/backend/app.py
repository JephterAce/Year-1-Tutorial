"""Isolated API starter for the secondary-school platform.

This intentionally exposes only health and clearly-labelled demo catalogue data.
It does not authenticate users, process payments, persist records or serve audio.
"""
from flask import Flask, jsonify

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

DEMO_CATALOGUE = [
    {"subject": "Mathematics", "title": "Quadratic equations", "term": "First term", "class_level": "SS2", "demo": True},
    {"subject": "Biology", "title": "Cell structure and organisation", "term": "First term", "class_level": "SS2", "demo": True},
    {"subject": "Chemistry", "title": "Atomic structure", "term": "First term", "class_level": "SS2", "demo": True},
    {"subject": "Physics", "title": "Motion and linear kinematics", "term": "First term", "class_level": "SS2", "demo": True},
    {"subject": "Further Mathematics", "title": "Functions and mappings", "term": "First term", "class_level": "SS2", "demo": True},
]


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "secondary-school-api", "mode": "starter"})


@app.get("/api/v1/catalogue")
def catalogue():
    return jsonify({
        "items": DEMO_CATALOGUE,
        "is_demo": True,
        "notice": "Illustrative sample data; not a verified curriculum or published lesson catalogue.",
    })


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "not_found", "message": "The requested resource was not found."}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "internal_error", "message": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    # Local development only. Use a production WSGI server in deployment.
    app.run(host="127.0.0.1", port=8000, debug=False)
