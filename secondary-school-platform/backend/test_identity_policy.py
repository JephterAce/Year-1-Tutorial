import unittest

from identity_policy import (
    create_one_time_token,
    hash_password,
    hash_session_id,
    normalise_email,
    validate_username,
    verify_password,
)


class IdentityPolicyTests(unittest.TestCase):
    def test_password_is_salted_and_verifiable(self):
        first = hash_password("correct horse battery staple")
        second = hash_password("correct horse battery staple")
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password(first, "correct horse battery staple"))
        self.assertFalse(verify_password(first, "wrong password"))

    def test_password_length_is_bounded(self):
        with self.assertRaises(ValueError):
            hash_password("short")
        with self.assertRaises(ValueError):
            hash_password("x" * 129)

    def test_email_is_normalised(self):
        self.assertEqual(normalise_email("  Learner@Example.com "), "learner@example.com")

    def test_invalid_email_is_rejected(self):
        for value in ("", "not-an-email", "a b@example.com", "x" * 255 + "@example.com"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalise_email(value)

    def test_username_is_validated_and_normalised(self):
        self.assertEqual(validate_username("Learner_01"), "learner_01")
        for value in ("ab", "has space", "name!", "x" * 25):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_username(value)

    def test_one_time_token_returns_only_digest_for_storage(self):
        raw, digest = create_one_time_token()
        import hashlib
        self.assertEqual(digest, hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(len(digest), 64)
        self.assertNotEqual(raw, digest)

    def test_session_identifier_hash_is_deterministic(self):
        self.assertEqual(hash_session_id("session-123"), hash_session_id("session-123"))
        self.assertNotEqual(hash_session_id("session-123"), hash_session_id("session-456"))


if __name__ == "__main__":
    unittest.main()
