"""Server-side timing policy for Learnwise timed assessments.

The browser countdown is display-only. The API must calculate and enforce
attempt deadlines from this policy.
"""
from dataclasses import dataclass

DEFAULT_SECONDS_PER_QUESTION = 36
QUESTION_TIME_OVERRIDES = {10: 7 * 60}
MIN_QUESTIONS_PER_ATTEMPT = 1
MAX_QUESTIONS_PER_ATTEMPT = 100


@dataclass(frozen=True)
class TestTiming:
    question_count: int
    time_limit_seconds: int

    @property
    def minutes(self):
        return self.time_limit_seconds // 60

    @property
    def seconds(self):
        return self.time_limit_seconds % 60

    @property
    def display(self):
        if self.seconds:
            return f"{self.minutes}m {self.seconds}s"
        return f"{self.minutes} minutes"


def calculate_test_timing(question_count: int) -> TestTiming:
    """Calculate approved time; ten questions receive the seven-minute exception."""
    if isinstance(question_count, bool) or not isinstance(question_count, int):
        raise ValueError("Question count must be a whole number.")
    if not MIN_QUESTIONS_PER_ATTEMPT <= question_count <= MAX_QUESTIONS_PER_ATTEMPT:
        raise ValueError(
            f"Question count must be between {MIN_QUESTIONS_PER_ATTEMPT} "
            f"and {MAX_QUESTIONS_PER_ATTEMPT}."
        )
    seconds = QUESTION_TIME_OVERRIDES.get(
        question_count, question_count * DEFAULT_SECONDS_PER_QUESTION
    )
    return TestTiming(question_count=question_count, time_limit_seconds=seconds)
