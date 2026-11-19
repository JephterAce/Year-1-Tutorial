import unittest
from payment_outbox import retry_delay_seconds, MAX_ATTEMPTS


class PaymentOutboxPolicyTests(unittest.TestCase):
    def test_exponential_backoff_is_bounded(self):
        self.assertEqual(retry_delay_seconds(1), 30)
        self.assertEqual(retry_delay_seconds(2), 60)
        self.assertEqual(retry_delay_seconds(3), 120)
        self.assertEqual(retry_delay_seconds(8), 3600)
        self.assertEqual(retry_delay_seconds(20), 3600)

    def test_invalid_attempt_count_rejected(self):
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                retry_delay_seconds(value)

    def test_attempt_limit_is_finite(self):
        self.assertEqual(MAX_ATTEMPTS, 8)


if __name__ == "__main__":
    unittest.main()
