"""Deterministic server-side grading for supported objective question types.

Never expose answer_key through student-facing question projections. Multiple-select
uses exact-set scoring in the first release; no partial-credit ambiguity.
"""
from decimal import Decimal, InvalidOperation


class GradingError(ValueError):
    pass


def _decimal(value):
    if isinstance(value, bool) or value is None:
        raise GradingError("A numeric answer is required.")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise GradingError("A numeric answer is required.")
    if not result.is_finite():
        raise GradingError("A finite numeric answer is required.")
    return result


def _normalise_text(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.casefold().split())


def grade_answer(question, answer):
    """Return correctness and awarded points; question data is trusted server-side."""
    if not isinstance(question, dict):
        raise GradingError("Question definition is invalid.")
    kind = question.get("question_type")
    key = question.get("answer_key")
    points = _decimal(question.get("points", 1))
    if points <= 0 or not isinstance(key, dict):
        raise GradingError("Question grading configuration is invalid.")

    correct = False
    if kind == "single_choice":
        expected = key.get("correct_option_id")
        if not isinstance(expected, str) or not expected:
            raise GradingError("Single-choice answer key is invalid.")
        correct = isinstance(answer, str) and answer == expected

    elif kind == "multiple_select":
        expected = key.get("correct_option_ids")
        if not isinstance(expected, list) or not expected or not all(isinstance(x, str) for x in expected):
            raise GradingError("Multiple-select answer key is invalid.")
        if len(set(expected)) != len(expected):
            raise GradingError("Multiple-select answer key contains duplicates.")
        if isinstance(answer, list) and all(isinstance(x, str) for x in answer):
            correct = len(set(answer)) == len(answer) and set(answer) == set(expected)

    elif kind == "true_false":
        expected = key.get("correct")
        if not isinstance(expected, bool):
            raise GradingError("True/false answer key is invalid.")
        correct = isinstance(answer, bool) and answer is expected

    elif kind == "numeric":
        expected = _decimal(key.get("value"))
        tolerance = _decimal(question.get("numeric_tolerance", 0))
        if tolerance < 0:
            raise GradingError("Numeric tolerance cannot be negative.")
        try:
            correct = abs(_decimal(answer) - expected) <= tolerance
        except GradingError:
            correct = False

    elif kind == "exact_text":
        expected = question.get("accepted_answers")
        if not isinstance(expected, list) or not expected or not all(isinstance(x, str) for x in expected):
            raise GradingError("Accepted text answers are not configured.")
        accepted = {_normalise_text(x) for x in expected if _normalise_text(x)}
        correct = _normalise_text(answer) in accepted if isinstance(answer, str) else False

    else:
        raise GradingError("Unsupported question type.")

    return {
        "is_correct": correct,
        "awarded_points": points if correct else Decimal("0"),
        "maximum_points": points,
    }


def grade_attempt(question_answers):
    """Grade an ordered sequence of (question, answer) pairs without leaking keys."""
    if not isinstance(question_answers, list) or not question_answers:
        raise GradingError("An attempt must contain at least one answerable question.")
    results = []
    score = Decimal("0")
    maximum = Decimal("0")
    for question, answer in question_answers:
        result = grade_answer(question, answer)
        score += result["awarded_points"]
        maximum += result["maximum_points"]
        results.append(result)
    percentage = (score * Decimal("100") / maximum).quantize(Decimal("0.01"))
    return {
        "score": score,
        "maximum_score": maximum,
        "percentage": percentage,
        "results": results,
    }
