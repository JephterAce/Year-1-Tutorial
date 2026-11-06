import os
import unittest
from datetime import date
from unittest.mock import patch

import ai_tutor_quota
from ai_tutor_quota import (
    TutorQuotaError,
    estimate_request_cost_microusd,
    reserve_tutor_usage,
)


class FakeConnection:
    def __init__(self, daily=None, monthly=None):
        self.daily = daily
        self.monthly = monthly or {"requests": 0, "cost": 0}
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        if "SELECT request_count,estimated_cost_microusd" in sql:
            return FakeCursor(self.daily)
        if "SELECT COALESCE(sum(request_count)" in sql:
            return FakeCursor(self.monthly)
        if "FROM ai_tutor_platform_usage WHERE usage_date=" in sql:
            return FakeCursor({"request_count":0,"estimated_cost_microusd":0})
        if "FROM ai_tutor_platform_usage" in sql:
            return FakeCursor({"cost":0})
        return FakeCursor(None)


class FakeCursor:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class TutorCostEstimateTests(unittest.TestCase):
    def test_reserves_input_and_maximum_output_cost(self):
        with patch.dict(os.environ, {
            "AI_INPUT_COST_MICROUSD_PER_1M_TOKENS": "1000000",
            "AI_OUTPUT_COST_MICROUSD_PER_1M_TOKENS": "2000000",
        }, clear=True):
            tokens, cost = estimate_request_cost_microusd("x" * 100, 600)
        self.assertEqual(tokens, 25)
        self.assertEqual(cost, 1225)

    def test_missing_pricing_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                estimate_request_cost_microusd("Explain atoms")


class TutorReservationTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "AI_INPUT_COST_MICROUSD_PER_1M_TOKENS": "1000000",
            "AI_OUTPUT_COST_MICROUSD_PER_1M_TOKENS": "2000000",
            "AI_TUTOR_DAILY_REQUEST_LIMIT": "2",
            "AI_TUTOR_MONTHLY_REQUEST_LIMIT": "10",
            "AI_TUTOR_DAILY_BUDGET_MICROUSD": "2000",
            "AI_TUTOR_MONTHLY_BUDGET_MICROUSD": "10000",
            "AI_TUTOR_PLATFORM_DAILY_BUDGET_MICROUSD": "5000",
            "AI_TUTOR_PLATFORM_MONTHLY_BUDGET_MICROUSD": "20000",
        }
        self.patch_env = patch.dict(os.environ, self.env, clear=True)
        self.patch_env.start()

    def tearDown(self):
        self.patch_env.stop()

    def test_reserves_usage_atomically(self):
        fake = FakeConnection()
        with patch.object(ai_tutor_quota, "connection", return_value=fake):
            result = reserve_tutor_usage(
                "student-1", "What is photosynthesis?", today=date(2026, 11, 6)
            )
        self.assertGreater(result["reserved_cost_microusd"], 0)
        self.assertTrue(any("pg_advisory_xact_lock" in sql for sql, _ in fake.calls))
        self.assertTrue(any("INSERT INTO student_ai_tutor_usage" in sql for sql, _ in fake.calls))
        self.assertTrue(any("INSERT INTO ai_tutor_platform_usage" in sql for sql, _ in fake.calls))

    def test_daily_request_limit_blocks_before_write(self):
        fake = FakeConnection(daily={"request_count": 2, "estimated_cost_microusd": 0})
        with patch.object(ai_tutor_quota, "connection", return_value=fake):
            with self.assertRaises(TutorQuotaError) as caught:
                reserve_tutor_usage("student-1", "Explain cells", today=date(2026, 11, 6))
        self.assertEqual(caught.exception.code, "request_limit_reached")
        self.assertFalse(any("INSERT INTO student_ai_tutor_usage" in sql for sql, _ in fake.calls))


    def test_platform_budget_limit_blocks_before_any_usage_write(self):
        class PlatformLimitedConnection(FakeConnection):
            def execute(self, sql, params=()):
                self.calls.append((sql, params))
                if "FROM student_ai_tutor_usage" in sql and "SELECT request_count" in sql:
                    return FakeCursor(None)
                if "FROM student_ai_tutor_usage" in sql and "COALESCE(sum" in sql:
                    return FakeCursor({"requests":0,"cost":0})
                if "FROM ai_tutor_platform_usage WHERE usage_date=" in sql:
                    return FakeCursor({"request_count":0,"estimated_cost_microusd":5000})
                if "FROM ai_tutor_platform_usage" in sql:
                    return FakeCursor({"cost":5000})
                return FakeCursor(None)
        fake=PlatformLimitedConnection()
        with patch.object(ai_tutor_quota,"connection",return_value=fake):
            with self.assertRaises(TutorQuotaError) as caught:
                reserve_tutor_usage("student-1","Explain cells",today=date(2026,11,6))
        self.assertEqual(caught.exception.code,"platform_budget_reached")
        self.assertFalse(any("INSERT INTO student_ai_tutor_usage" in sql for sql,_ in fake.calls))
        self.assertFalse(any("INSERT INTO ai_tutor_platform_usage" in sql for sql,_ in fake.calls))

    def test_monthly_spend_limit_blocks_before_write(self):
        fake = FakeConnection(monthly={"requests": 0, "cost": 9999})
        with patch.object(ai_tutor_quota, "connection", return_value=fake):
            with self.assertRaises(TutorQuotaError) as caught:
                reserve_tutor_usage("student-1", "Explain cells", today=date(2026, 11, 6))
        self.assertEqual(caught.exception.code, "spend_limit_reached")
        self.assertFalse(any("INSERT INTO student_ai_tutor_usage" in sql for sql, _ in fake.calls))


if __name__ == "__main__":
    unittest.main()
