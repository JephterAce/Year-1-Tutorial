import unittest

from assessment_policy import calculate_test_timing


class TestAssessmentTiming(unittest.TestCase):
    def test_approved_question_count_examples(self):
        expected = {5: 180, 10: 420, 50: 1800, 100: 3600}
        for count, seconds in expected.items():
            with self.subTest(count=count):
                timing = calculate_test_timing(count)
                self.assertEqual(timing.question_count, count)
                self.assertEqual(timing.time_limit_seconds, seconds)

    def test_ten_question_override_is_exactly_seven_minutes(self):
        self.assertEqual(calculate_test_timing(10).display, "7 minutes")

    def test_non_whole_number_and_bool_rejected(self):
        for value in (0, -1, 1.5, "10", True, None, 101):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_test_timing(value)

    def test_display_handles_minutes_and_seconds(self):
        self.assertEqual(calculate_test_timing(5).display, "3 minutes")
        self.assertEqual(calculate_test_timing(1).display, "36s")
        self.assertEqual(calculate_test_timing(2).display, "1m 12s")


if __name__ == "__main__":
    unittest.main()
