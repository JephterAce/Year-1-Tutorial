"""Transactional assessment-attempt execution.

All clocks, ownership checks, snapshots, answer keys and grading remain server-side.
The service is intentionally database-backed; no demo/fallback attempts are allowed.
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from psycopg.types.json import Jsonb

from database import connection
from assessment_policy import calculate_test_timing
from assessment_grading import grade_answer


class AttemptError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


POLICY_VERSION = "learnwise-test-briefing-v1"
DEBOUNCE_SECONDS = 2


def _json(value):
    return value if isinstance(value, dict) else (value or {})


def _public_question(row):
    prompt = _json(row["question_snapshot"]).get("prompt", {})
    raw_options = _json(row["question_snapshot"]).get("options")
    options = ([{"id": item.get("id"), "text": item.get("text")}
                for item in raw_options if isinstance(item, dict)
                and isinstance(item.get("id"), str) and isinstance(item.get("text"), str)]
               if isinstance(raw_options, list) else None)
    return {
        "id": str(row["question_id"]),
        "type": _json(row["question_snapshot"]).get("question_type"),
        "prompt": prompt,
        "options": options,
        "points": str(row["points_snapshot"]),
        "display_order": row["display_order"],
    }


def create_attempt(student_id, assessment_id, question_count):
    if isinstance(question_count, bool) or not isinstance(question_count, int):
        raise AttemptError("invalid_question_count", "Choose a valid question count.")
    with connection() as conn:
        assessment = conn.execute(
            """SELECT id, version, class_level, status, allowed_question_counts,
                      max_attempts, available_from, available_until
               FROM assessments WHERE id=%s FOR SHARE""", (assessment_id,)
        ).fetchone()
        if not assessment or assessment["status"] != "published":
            raise AttemptError("assessment_unavailable", "This assessment is not available.", 404)
        if question_count not in assessment["allowed_question_counts"]:
            raise AttemptError("invalid_question_count", "That question count is not offered.")
        now = datetime.now(timezone.utc)
        if assessment["available_from"] and now < assessment["available_from"]:
            raise AttemptError("not_open", "This assessment has not opened.", 409)
        if assessment["available_until"] and now >= assessment["available_until"]:
            raise AttemptError("closed", "This assessment has closed.", 409)
        student = conn.execute("SELECT class_level FROM students WHERE id=%s", (student_id,)).fetchone()
        if not student or student["class_level"] != assessment["class_level"]:
            raise AttemptError("not_eligible", "You are not eligible for this assessment.", 403)
        used = conn.execute(
            """SELECT count(*) AS n FROM assessment_attempts
               WHERE assessment_id=%s AND student_id=%s
                 AND status <> 'briefing'""", (assessment_id, student_id)
        ).fetchone()["n"]
        if used >= assessment["max_attempts"]:
            raise AttemptError("attempt_limit", "The attempt limit has been reached.", 409)
        timing = calculate_test_timing(question_count)
        attempt = conn.execute(
            """INSERT INTO assessment_attempts
               (assessment_id,assessment_version,student_id,question_count,
                time_limit_seconds,policy_version,status)
               VALUES (%s,%s,%s,%s,%s,%s,'briefing') RETURNING id""",
            (assessment_id, assessment["version"], student_id, question_count,
             timing.time_limit_seconds, POLICY_VERSION)
        ).fetchone()
        return {"attempt_id": str(attempt["id"]), "status": "briefing",
                "question_count": question_count, "time_limit_seconds": timing.time_limit_seconds,
                "policy_version": POLICY_VERSION}


def start_attempt(student_id, attempt_id, accepted, policy_version):
    if accepted is not True or policy_version != POLICY_VERSION:
        raise AttemptError("briefing_acceptance_required", "Review and accept the test briefing.")
    with connection() as conn:
        attempt = conn.execute(
            """SELECT a.*, s.status AS assessment_status
               FROM assessment_attempts a JOIN assessments s ON s.id=a.assessment_id
               WHERE a.id=%s AND a.student_id=%s FOR UPDATE OF a""",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            raise AttemptError("not_found", "Attempt not found.", 404)
        if attempt["status"] == "in_progress":
            return _attempt_state(conn, attempt_id, student_id)
        if attempt["status"] != "briefing" or attempt["assessment_status"] != "published":
            raise AttemptError("invalid_state", "This attempt cannot be started.", 409)
        questions = conn.execute(
            """SELECT id, question_type, prompt, options, answer_key, points,
                      numeric_tolerance, accepted_answers
               FROM assessment_questions
               WHERE assessment_id=%s AND is_active=true
               ORDER BY random() LIMIT %s""",
            (attempt["assessment_id"], attempt["question_count"])
        ).fetchall()
        if len(questions) != attempt["question_count"]:
            raise AttemptError("question_pool_insufficient", "This test is not ready yet.", 409)
        for index, q in enumerate(questions, start=1):
            snapshot = {"question_type": q["question_type"], "prompt": q["prompt"],
                        "options": q["options"]}
            conn.execute(
                """INSERT INTO assessment_attempt_questions
                   (attempt_id,question_id,display_order,question_snapshot,
                    answer_key_snapshot,points_snapshot,numeric_tolerance_snapshot,
                    accepted_answers_snapshot)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (attempt_id, q["id"], index, Jsonb(snapshot), Jsonb(q["answer_key"]),
                 q["points"], q["numeric_tolerance"],
                 Jsonb(q["accepted_answers"]) if q["accepted_answers"] is not None else None)
            )
        now = datetime.now(timezone.utc)
        deadline = now + timedelta(seconds=attempt["time_limit_seconds"])
        conn.execute(
            """UPDATE assessment_attempts SET status='in_progress',
               agreement_recorded_at=%s, started_at=%s, deadline_at=%s
               WHERE id=%s""", (now, now, deadline, attempt_id)
        )
        return _attempt_state(conn, attempt_id, student_id)


def _attempt_state(conn, attempt_id, student_id):
    attempt = conn.execute(
        """SELECT id,status,question_count,time_limit_seconds,started_at,deadline_at,
                  integrity_incidents,integrity_review_required
           FROM assessment_attempts WHERE id=%s AND student_id=%s""",
        (attempt_id, student_id)
    ).fetchone()
    if not attempt:
        raise AttemptError("not_found", "Attempt not found.", 404)
    questions = conn.execute(
        """SELECT question_id,display_order,question_snapshot,points_snapshot
           FROM assessment_attempt_questions WHERE attempt_id=%s ORDER BY display_order""",
        (attempt_id,)
    ).fetchall()
    answers = conn.execute(
        "SELECT question_id,answer FROM assessment_answers WHERE attempt_id=%s", (attempt_id,)
    ).fetchall()
    return {
        "attempt_id": str(attempt["id"]), "status": attempt["status"],
        "question_count": attempt["question_count"], "time_limit_seconds": attempt["time_limit_seconds"],
        "started_at": attempt["started_at"].isoformat() if attempt["started_at"] else None,
        "deadline_at": attempt["deadline_at"].isoformat() if attempt["deadline_at"] else None,
        "integrity_incidents": attempt["integrity_incidents"],
        "integrity_review_required": attempt["integrity_review_required"],
        "questions": [_public_question(q) for q in questions],
        "answers": {str(a["question_id"]): a["answer"] for a in answers},
    }


def get_attempt(student_id, attempt_id):
    with connection() as conn:
        return _attempt_state(conn, attempt_id, student_id)


def _finalize(conn, attempt, status):
    pairs = conn.execute(
        """SELECT aq.question_id,aq.answer_key_snapshot,aq.points_snapshot,
                  aq.numeric_tolerance_snapshot,aq.accepted_answers_snapshot,
                  aa.answer,aq.question_snapshot
           FROM assessment_attempt_questions aq
           LEFT JOIN assessment_answers aa
             ON aa.attempt_id=aq.attempt_id AND aa.question_id=aq.question_id
           WHERE aq.attempt_id=%s ORDER BY aq.display_order""", (attempt["id"],)
    ).fetchall()
    score, maximum = Decimal("0"), Decimal("0")
    for item in pairs:
        snap = _json(item["question_snapshot"])
        q = {"question_type": snap.get("question_type"),
             "answer_key": _json(item["answer_key_snapshot"]),
             "points": item["points_snapshot"],
             "numeric_tolerance": item["numeric_tolerance_snapshot"] if item["numeric_tolerance_snapshot"] is not None else 0,
             "accepted_answers": item["accepted_answers_snapshot"]}
        result = grade_answer(q, item["answer"])
        score += result["awarded_points"]
        maximum += result["maximum_points"]
        conn.execute(
            """INSERT INTO assessment_answers
               (attempt_id,question_id,answer,is_correct,awarded_points)
               VALUES (%s,%s,%s,%s,%s)
               ON CONFLICT (attempt_id,question_id) DO UPDATE
               SET is_correct=EXCLUDED.is_correct,awarded_points=EXCLUDED.awarded_points""",
            (attempt["id"], item["question_id"], Jsonb(item["answer"]) if item["answer"] is not None else None,
             result["is_correct"], result["awarded_points"])
        )
    percent = (score * Decimal("100") / maximum).quantize(Decimal("0.01")) if maximum else Decimal("0")
    assessment = conn.execute(
        "SELECT pass_mark_percent FROM assessments WHERE id=%s", (attempt["assessment_id"],)
    ).fetchone()
    conn.execute(
        """UPDATE assessment_attempts SET status=%s,submitted_at=now(),graded_at=now(),
           score=%s,maximum_score=%s,percentage=%s,passed=%s
           WHERE id=%s""",
        (status, score, maximum, percent, percent >= assessment["pass_mark_percent"], attempt["id"])
    )
    return {"attempt_id": str(attempt["id"]), "status": status,
            "score": str(score), "maximum_score": str(maximum),
            "percentage": str(percent), "integrity_review_required": attempt["integrity_review_required"]}


def save_answer(student_id, attempt_id, question_id, answer):
    with connection() as conn:
        attempt = conn.execute(
            "SELECT * FROM assessment_attempts WHERE id=%s AND student_id=%s FOR UPDATE",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            raise AttemptError("not_found", "Attempt not found.", 404)
        if attempt["status"] != "in_progress":
            raise AttemptError("not_in_progress", "This test is no longer accepting answers.", 409)
        if datetime.now(timezone.utc) >= attempt["deadline_at"]:
            return _finalize(conn, attempt, "expired")
        q = conn.execute(
            """SELECT question_id,question_snapshot FROM assessment_attempt_questions
               WHERE attempt_id=%s AND question_id=%s""", (attempt_id, question_id)
        ).fetchone()
        if not q:
            raise AttemptError("invalid_question", "Question does not belong to this attempt.")
        snap = _json(q["question_snapshot"])
        kind = snap.get("question_type")
        if kind in ("single_choice", "exact_text") and answer is not None and not isinstance(answer, str):
            raise AttemptError("invalid_answer", "Answer format is invalid.")
        if kind == "multiple_select" and (not isinstance(answer, list) or not all(isinstance(x, str) for x in answer)):
            raise AttemptError("invalid_answer", "Select one or more valid options.")
        if kind == "true_false" and not isinstance(answer, bool):
            raise AttemptError("invalid_answer", "Choose true or false.")
        if kind == "numeric" and (answer is not None and (isinstance(answer, bool) or not isinstance(answer, (str, int, float)))):
            raise AttemptError("invalid_answer", "Enter a numeric answer.")
        conn.execute(
            """INSERT INTO assessment_answers(attempt_id,question_id,answer)
               VALUES (%s,%s,%s) ON CONFLICT (attempt_id,question_id) DO UPDATE
               SET answer=EXCLUDED.answer,saved_at=now()""",
            (attempt_id, question_id, Jsonb(answer) if answer is not None else None)
        )
        return {"saved": True, "saved_at": datetime.now(timezone.utc).isoformat()}


def submit_attempt(student_id, attempt_id):
    with connection() as conn:
        attempt = conn.execute(
            "SELECT * FROM assessment_attempts WHERE id=%s AND student_id=%s FOR UPDATE",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            raise AttemptError("not_found", "Attempt not found.", 404)
        if attempt["status"] in ("submitted", "expired", "terminated_integrity", "graded", "under_review"):
            return {"attempt_id": str(attempt_id), "status": attempt["status"],
                    "score": str(attempt["score"]) if attempt["score"] is not None else None}
        if attempt["status"] != "in_progress":
            raise AttemptError("not_in_progress", "Start the test before submitting.", 409)
        status = "expired" if datetime.now(timezone.utc) >= attempt["deadline_at"] else "submitted"
        return _finalize(conn, attempt, status)


def record_integrity_event(student_id, attempt_id, event_type):
    allowed = {"visibility_hidden", "fullscreen_exit", "window_blur"}
    if event_type not in allowed:
        raise AttemptError("invalid_event", "Unsupported integrity event.")
    with connection() as conn:
        attempt = conn.execute(
            "SELECT * FROM assessment_attempts WHERE id=%s AND student_id=%s FOR UPDATE",
            (attempt_id, student_id)
        ).fetchone()
        if not attempt:
            raise AttemptError("not_found", "Attempt not found.", 404)
        if attempt["status"] != "in_progress":
            raise AttemptError("not_in_progress", "This test is no longer active.", 409)
        now = datetime.now(timezone.utc)
        if now >= attempt["deadline_at"]:
            return _finalize(conn, attempt, "expired")
        last = conn.execute(
            """SELECT server_received_at FROM assessment_integrity_events
               WHERE attempt_id=%s AND event_type IN ('visibility_hidden','fullscreen_exit','window_blur')
               ORDER BY server_received_at DESC LIMIT 1""", (attempt_id,)
        ).fetchone()
        if last and (now - last["server_received_at"]).total_seconds() <= DEBOUNCE_SECONDS:
            return {"recorded": False, "debounced": True,
                    "integrity_incidents": attempt["integrity_incidents"]}
        incident = min(3, attempt["integrity_incidents"] + 1)
        conn.execute(
            """INSERT INTO assessment_integrity_events(attempt_id,event_type,incident_number)
               VALUES (%s,%s,%s)""", (attempt_id, event_type, incident)
        )
        if incident >= 3:
            conn.execute(
                "UPDATE assessment_attempts SET integrity_incidents=3,integrity_review_required=true WHERE id=%s",
                (attempt_id,)
            )
            conn.execute(
                """INSERT INTO assessment_integrity_events(attempt_id,event_type,incident_number)
                   VALUES (%s,'terminated',3)""", (attempt_id,)
            )
            attempt["integrity_review_required"] = True
            result = _finalize(conn, attempt, "terminated_integrity")
            result["message"] = "Integrity review required. This event is not a finding of misconduct."
            return result
        conn.execute(
            "UPDATE assessment_attempts SET integrity_incidents=%s WHERE id=%s",
            (incident, attempt_id)
        )
        return {"recorded": True, "warning": incident, "integrity_incidents": incident,
                "message": "Please return to the test. The timer continues."}
