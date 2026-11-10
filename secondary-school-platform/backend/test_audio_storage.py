import io
import unittest
from unittest.mock import Mock, patch

import audio_storage
from audio_storage import AudioStorageError


class PrivateAudioStorageTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "AWS_ACCESS_KEY_ID": "test-access",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_ENDPOINT_URL_S3": "https://storage.example.invalid",
            "AWS_REGION": "eu-central-1",
            "AUDIO_STORAGE_BUCKET": "learnwise-private-audio",
        }

    def test_storage_diagnostics_report_precedence_without_exposing_credentials(self):
        env = {
            "AUDIO_STORAGE_ACCESS_KEY_ID": "new-access",
            "AUDIO_STORAGE_SECRET_ACCESS_KEY": "new-secret",
            "AUDIO_STORAGE_ENDPOINT_URL_S3": "https://account123.r2.cloudflarestorage.com",
            "AUDIO_STORAGE_BUCKET": "learnwise-private-audio",
            "AWS_ACCESS_KEY_ID": "old-access",
            "AWS_SECRET_ACCESS_KEY": "old-secret",
            "AWS_ENDPOINT_URL_S3": "https://old-account.r2.cloudflarestorage.com",
        }
        with patch.dict("os.environ", env, clear=True):
            diagnostic = audio_storage.storage_config_diagnostics()
        self.assertEqual(diagnostic["access_key_source"], "AUDIO_STORAGE_ACCESS_KEY_ID")
        self.assertEqual(diagnostic["secret_key_source"], "AUDIO_STORAGE_SECRET_ACCESS_KEY")
        self.assertEqual(diagnostic["endpoint_account_id"], "account123")
        self.assertTrue(diagnostic["access_key_aliases_conflict"])
        self.assertTrue(diagnostic["secret_key_aliases_conflict"])
        self.assertNotIn("new-access", str(diagnostic))
        self.assertNotIn("new-secret", str(diagnostic))

    def test_r2_endpoint_always_uses_auto_region_even_with_legacy_aws_region(self):
        env = {
            "AUDIO_STORAGE_ACCESS_KEY_ID": "audio-access",
            "AUDIO_STORAGE_SECRET_ACCESS_KEY": "audio-secret",
            "AUDIO_STORAGE_ENDPOINT_URL_S3": "https://account.r2.cloudflarestorage.com",
            "AUDIO_STORAGE_REGION": "eu-central-1",
            "AUDIO_STORAGE_BUCKET": "learnwise-private-audio",
            "AWS_REGION": "us-east-1",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = audio_storage.storage_config()
        self.assertEqual(cfg["region"], "auto")
        self.assertEqual(cfg["bucket"], "learnwise-private-audio")

    def test_non_r2_provider_keeps_its_configured_region(self):
        with patch.dict("os.environ", self.env, clear=True):
            cfg = audio_storage.storage_config()
        self.assertEqual(cfg["region"], "eu-central-1")

    def test_upload_rejects_unsupported_type_and_oversize(self):
        with patch.dict("os.environ", self.env, clear=True):
            with self.assertRaises(AudioStorageError):
                audio_storage.put_private_audio_object("topics/a/audio.mp3", io.BytesIO(b"x"), "text/plain", 1)
            with self.assertRaises(AudioStorageError):
                audio_storage.put_private_audio_object("topics/a/audio.mp3", io.BytesIO(b"x"), "audio/mpeg", 100 * 1024 * 1024 + 1)

    def test_upload_writes_private_object_without_public_acl(self):
        client = Mock()
        client.put_object.return_value = {"ETag": '"etag-123"'}
        with patch.dict("os.environ", self.env, clear=True), patch.object(audio_storage, "_s3_client", return_value=client):
            result = audio_storage.put_private_audio_object("topics/topic-1/teacher_audio/a.mp3", io.BytesIO(b"audio"), "audio/mpeg", 5)
        self.assertEqual(result, "etag-123")
        kwargs = client.put_object.call_args.kwargs
        self.assertEqual(kwargs["Bucket"], "learnwise-private-audio")
        self.assertEqual(kwargs["ContentLength"], 5)
        self.assertNotIn("ACL", kwargs)

    def test_download_forwards_single_byte_range(self):
        client = Mock()
        client.get_object.return_value = {"Body": object(), "ContentLength": 4, "ContentRange": "bytes 0-3/10"}
        with patch.dict("os.environ", self.env, clear=True), patch.object(audio_storage, "_s3_client", return_value=client):
            result = audio_storage.get_private_audio_object("topics/topic-1/audio.mp3", "bytes=0-3")
        self.assertEqual(result["ContentRange"], "bytes 0-3/10")
        self.assertEqual(client.get_object.call_args.kwargs["Range"], "bytes=0-3")

    def test_download_rejects_malformed_ranges_and_path_traversal(self):
        with patch.dict("os.environ", self.env, clear=True):
            for key in ("../secret.mp3", "/absolute.mp3", "topics//audio.mp3", "topics/./audio.mp3"):
                with self.subTest(key=key), self.assertRaises(AudioStorageError):
                    audio_storage.get_private_audio_object(key)
            for value in ("bytes=0-1,4-5", "bytes=abc-def", "bytes=-", "bytes=8-2", "bytes=-0"):
                with self.subTest(value=value), self.assertRaises(AudioStorageError):
                    audio_storage.get_private_audio_object("audio.mp3", value)

    def test_download_accepts_open_ended_and_suffix_ranges(self):
        client = Mock()
        client.get_object.return_value = {"Body": object()}
        with patch.dict("os.environ", self.env, clear=True), patch.object(audio_storage, "_s3_client", return_value=client):
            audio_storage.get_private_audio_object("audio.mp3", "bytes=10-")
            self.assertEqual(client.get_object.call_args.kwargs["Range"], "bytes=10-")
            audio_storage.get_private_audio_object("audio.mp3", "bytes=-500")
            self.assertEqual(client.get_object.call_args.kwargs["Range"], "bytes=-500")

    def test_private_object_can_be_removed_after_database_failure(self):
        client = Mock()
        with patch.dict("os.environ", self.env, clear=True), patch.object(audio_storage, "_s3_client", return_value=client):
            audio_storage.delete_private_audio_object("topics/topic-1/audio.mp3")
        client.delete_object.assert_called_once_with(Bucket="learnwise-private-audio", Key="topics/topic-1/audio.mp3")


if __name__ == "__main__":
    unittest.main()
