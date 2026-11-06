"""Transactional per-student AI tutor request and spend reservations."""
import math
import os
from datetime import date, datetime, timezone
from database import connection


class TutorQuotaError(ValueError):
    def __init__(self, code, message, status=429):
        super().__init__(message)
        self.code, self.status = code, status


def _positive_int(name, default):
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise RuntimeError(f"{name} must be a positive integer") from None
    if value < 1:
        raise RuntimeError(f"{name} must be a positive integer")
    return value


def estimate_request_cost_microusd(input_text, output_token_reservation=600):
    """Conservative upper-bound cost estimate; reserves the full output allowance."""
    input_tokens = max(1, math.ceil(len(input_text) / 4))
    input_rate = _positive_int("AI_INPUT_COST_MICROUSD_PER_1M_TOKENS", 0)
    output_rate = _positive_int("AI_OUTPUT_COST_MICROUSD_PER_1M_TOKENS", 0)
    # A missing/zero rate must never silently turn cost control off.
    return (
        input_tokens,
        math.ceil(input_tokens * input_rate / 1_000_000)
        + math.ceil(output_token_reservation * output_rate / 1_000_000),
    )


def reserve_tutor_usage(student_id, input_text, output_token_reservation=600, today=None):
    """Atomically enforce daily/monthly request and estimated-spend limits."""
    if not student_id:
        raise TutorQuotaError("student_required", "A verified student session is required.", 401)
    usage_day = today or datetime.now(timezone.utc).date()
    month_start = usage_day.replace(day=1)
    input_tokens, cost = estimate_request_cost_microusd(input_text, output_token_reservation)
    daily_requests = _positive_int("AI_TUTOR_DAILY_REQUEST_LIMIT", 20)
    monthly_requests = _positive_int("AI_TUTOR_MONTHLY_REQUEST_LIMIT", 300)
    daily_budget = _positive_int("AI_TUTOR_DAILY_BUDGET_MICROUSD", 1_000_000)
    monthly_budget = _positive_int("AI_TUTOR_MONTHLY_BUDGET_MICROUSD", 10_000_000)

    with connection() as conn:
        # Serialize a student's reservation transactions to prevent concurrent overspend.
        conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (str(student_id),))
        daily = conn.execute(
            """SELECT request_count,estimated_cost_microusd
               FROM student_ai_tutor_usage
               WHERE student_id=%s AND usage_date=%s FOR UPDATE""",
            (student_id, usage_day),
        ).fetchone()
        monthly = conn.execute(
            """SELECT COALESCE(sum(request_count),0) AS requests,
                      COALESCE(sum(estimated_cost_microusd),0) AS cost
               FROM student_ai_tutor_usage
               WHERE student_id=%s AND usage_date >= %s AND usage_date <= %s""",
            (student_id, month_start, usage_day),
        ).fetchone()
        daily_count = daily["request_count"] if daily else 0
        daily_cost = daily["estimated_cost_microusd"] if daily else 0
        if daily_count >= daily_requests or monthly["requests"] >= monthly_requests:
            raise TutorQuotaError("request_limit_reached", "Your AI teacher usage limit has been reached. Please try again later.")
        if daily_cost + cost > daily_budget or monthly["cost"] + cost > monthly_budget:
            raise TutorQuotaError("spend_limit_reached", "The AI teacher has reached its usage budget for now. Please try again later.")
        conn.execute(
            """INSERT INTO student_ai_tutor_usage
                 (student_id,usage_date,request_count,estimated_cost_microusd,
                  estimated_input_tokens,reserved_output_tokens)
               VALUES (%s,%s,1,%s,%s,%s)
               ON CONFLICT(student_id,usage_date) DO UPDATE SET
                 request_count=student_ai_tutor_usage.request_count+1,
                 estimated_cost_microusd=student_ai_tutor_usage.estimated_cost_microusd+EXCLUDED.estimated_cost_microusd,
                 estimated_input_tokens=student_ai_tutor_usage.estimated_input_tokens+EXCLUDED.estimated_input_tokens,
                 reserved_output_tokens=student_ai_tutor_usage.reserved_output_tokens+EXCLUDED.reserved_output_tokens,
                 updated_at=now()""",
            (student_id, usage_day, cost, input_tokens, output_token_reservation),
        )
    return {"reserved_cost_microusd": cost, "estimated_input_tokens": input_tokens}
