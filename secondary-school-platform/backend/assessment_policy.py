"""Server-side policy helpers for timed assessments.

The API must use these values to calculate authoritative attempt deadlines.
The browser countdown is display-only.
"""
from dataclasses import dataclass

SECONDS_PER_QUESTION = 36
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
    """Calculate 36 seconds per question; reject bools and invalid counts."""
    if isinstance(question_count, bool) or not isinstance(question_count, int):
        raise ValueError("Question count must be a whole number.")
    if not MIN_QUESTIONS_PER_ATTEMPT <= question_count <= MAX_QUESTIONS_PER_ATTEMPT:
        raise ValueError(
            f"Question count must be between {MIN_QUESTIONS_PER_ATTEMPT} "
            f"and {MAX_QUESTIONS_PER_ATTEMPT}."
        )
    return TestTiming(
        question_count=question_count,
        time_limit_seconds=question_count * SECONDS_PER_QUESTION,
    )
