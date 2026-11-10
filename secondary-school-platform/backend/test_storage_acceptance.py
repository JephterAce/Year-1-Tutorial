import os
import unittest
from unittest.mock import patch

from app import app
from admin_policy import AdminPrincipal


class StagingStorageDiagnosticRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.flags = {"APP_ENV": "staging", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "true"}
        self.owner = {
            "admin_id": "owner-id", "email": "owner@example.test", "role": "owner",
            "principal": AdminPrincipal("owner-id", "owner", True),
        }

    def test_storage_diagnostic_is_hidden_when_flag_is_disabled(self):
        with patch.dict(os.environ, {"APP_ENV": "staging", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "false"}):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 404)

    def test_storage_diagnostic_is_hidden_outside_staging(self):
        with patch.dict(os.environ, {"APP_ENV": "production", "STAGING_STORAGE_DIAGNOSTICS_ENABLED": "true"}):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 404)

    def test_storage_diagnostic_requires_admin_session_and_csrf(self):
        with patch.dict(os.environ, self.flags), patch("app._current_admin", return_value=None):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 401)

    def test_storage_diagnostic_rejects_request_body(self):
        with patch.dict(os.environ, self.flags), patch("app._current_admin", return_value=self.owner):
            response = self.client.post("/api/v1/admin/diagnostics/storage", json={"bucket": "override"})
        self.assertEqual(response.status_code, 400)

    def test_storage_diagnostic_records_synthetic_results(self):
        result = {
            "passed": True,
            "results": {
                "audio": {"configured": True, "passed": True, "upload": True, "retrieval": True,
                          "checksum_match": True, "unsigned_access_denied": True, "deletion": True,
                          "sha256": "a" * 64},
                "r2_exports": {"configured": True, "passed": True, "upload": True, "retrieval": True,
                               "checksum_match": True, "unsigned_access_denied": True, "deletion": True,
                               "sha256": "b" * 64},
            },
        }
        with patch.dict(os.environ, self.flags), \
             patch("app._current_admin", return_value=self.owner), \
             patch("admin_auth.reserve_admin_storage_diagnostic"), \
             patch("storage_acceptance.run_private_storage_acceptance", return_value=result), \
             patch("admin_auth.record_admin_audit") as audit:
            response = self.client.post("/api/v1/admin/diagnostics/storage", json={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["passed"])
        audit.assert_called_once()
        self.assertNotIn("secret_access_key", str(audit.call_args))

    def test_storage_diagnostic_returns_503_if_a_bucket_fails(self):
        result = {"passed": False, "results": {
            "audio": {"configured": True, "passed": False, "failure_class": "EndpointConnectionError"},
            "r2_exports": {"configured": True, "passed": True},
        }}
        with patch.dict(os.environ, self.flags), \
             patch("app._current_admin", return_value=self.owner), \
             patch("admin_auth.reserve_admin_storage_diagnostic"), \
             patch("storage_acceptance.run_private_storage_acceptance", return_value=result), \
             patch("admin_auth.record_admin_audit"):
            response = self.client.post("/api/v1/admin/diagnostics/storage")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.get_json()["passed"])



class StorageProbeUnitTests(unittest.TestCase):
    def test_generic_s3_probe_uploads_checksums_denies_unsigned_and_deletes(self):
        import io
        from unittest.mock import Mock
        from botocore.exceptions import ClientError
        from storage_acceptance import _probe_s3

        payload = b"synthetic-storage-payload"
        client = Mock()
        client.get_object.return_value = {"Body": io.BytesIO(payload)}
        client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
            "HeadObject",
        )
        with patch("storage_acceptance._unsigned_http_denied", return_value=True):
            result = _probe_s3(client, "https://storage.example.test", "auto",
                               "private-bucket", "qa-acceptance/test.wav", payload)
        self.assertTrue(result["upload"])
        self.assertTrue(result["retrieval"])
        self.assertTrue(result["checksum_match"])
        self.assertTrue(result["unsigned_access_denied"])
        self.assertTrue(result["deletion"])
        client.delete_object.assert_called_once()

    def test_audio_probe_uses_application_storage_adapter(self):
        import io
        from unittest.mock import Mock
        from botocore.exceptions import ClientError
        from storage_acceptance import _probe_audio

        payload = b"synthetic-audio"
        cfg = {
            "endpoint_url": "https://storage.example.test",
            "region": "eu-central-1",
            "bucket": "private-audio",
        }
        client = Mock()
        client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
            "HeadObject",
        )
        with patch("audio_storage.put_private_audio_object"), \
             patch("audio_storage.get_private_audio_object", return_value={"Body": io.BytesIO(payload)}), \
             patch("audio_storage.delete_private_audio_object") as delete, \
             patch("storage_acceptance._unsigned_denied", return_value=True):
            result = _probe_audio(cfg, client, "qa-acceptance/audio.wav", payload)
        self.assertTrue(result["passed"] if "passed" in result else result["checksum_match"])
        delete.assert_called_once_with("qa-acceptance/audio.wav")


    def test_safe_failure_includes_bounded_provider_context_and_redacts_long_values(self):
        from botocore.exceptions import ClientError
        from storage_acceptance import _safe_failure

        exc = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "SECRET_VALUE_DO_NOT_EXPOSE"},
             "ResponseMetadata": {"HTTPStatusCode": 403}},
            "PutObject",
        )
        result = _safe_failure(exc, "r2_storage_transfer")
        self.assertEqual(result["provider_code"], "AccessDenied")
        self.assertEqual(result["http_status"], 403)
        self.assertFalse(result["retryable"])
        self.assertEqual(result["provider_operation"], "PutObject")
        self.assertEqual(result["provider_message"], "[redacted]")
        self.assertNotIn("SECRET_VALUE_DO_NOT_EXPOSE", str(result))

    def test_r2_config_accepts_documented_r2_aliases(self):
        from storage_acceptance import run_private_storage_acceptance
        env = {
            "APP_ENV": "staging",
            "R2_ACCESS_KEY_ID": "access-id",
            "R2_SECRET_ACCESS_KEY": "secret-value",
            "R2_ENDPOINT_URL": "https://account.r2.cloudflarestorage.com",
            "R2_BUCKET_NAME": "private-export-bucket",
            "R2_REGION": "auto",
        }
        with patch.dict(os.environ, env, clear=True), \
             patch("audio_storage.storage_config", side_effect=RuntimeError("audio not configured")), \
             patch("storage_acceptance._probe_s3", return_value={
                 "configured": True, "upload": True, "retrieval": True,
                 "checksum_match": True, "unsigned_access_denied": True,
                 "deletion": True, "sha256": "a" * 64,
             }) as probe:
            result = run_private_storage_acceptance()
        self.assertTrue(result["results"]["r2_exports"]["passed"])
        probe.assert_called_once()


    def test_r2_upload_failure_reports_exact_safe_operation_phase(self):
        from unittest.mock import Mock
        from botocore.exceptions import ClientError
        from storage_acceptance import _probe_s3, _safe_failure, StorageProbeStepError

        client = Mock()
        client.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "private provider detail"},
             "ResponseMetadata": {"HTTPStatusCode": 403}},
            "PutObject",
        )
        with self.assertRaises(StorageProbeStepError) as caught:
            _probe_s3(client, "https://storage.example.test", "auto",
                      "private-bucket", "qa-acceptance/test.wav", b"synthetic")
        self.assertEqual(caught.exception.failure_phase, "r2_upload")
        safe = _safe_failure(caught.exception, caught.exception.failure_phase)
        self.assertEqual(safe["provider_code"], "AccessDenied")
        self.assertEqual(safe["http_status"], 403)
        self.assertNotIn("private provider detail", str(safe))

    def test_audio_upload_failure_reports_exact_safe_operation_phase(self):
        import io
        from unittest.mock import Mock, patch
        from botocore.exceptions import ClientError
        from storage_acceptance import _probe_audio, _safe_failure, StorageProbeStepError

        provider_error = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "private provider detail"},
             "ResponseMetadata": {"HTTPStatusCode": 403}},
            "PutObject",
        )
        cfg = {"endpoint_url": "https://storage.example.test", "region": "auto", "bucket": "private-audio"}
        with patch("audio_storage.put_private_audio_object", side_effect=provider_error):
            with self.assertRaises(StorageProbeStepError) as caught:
                _probe_audio(cfg, Mock(), "qa-acceptance/audio.wav", b"synthetic")
        self.assertEqual(caught.exception.failure_phase, "audio_upload")
        safe = _safe_failure(caught.exception, caught.exception.failure_phase)
        self.assertEqual(safe["provider_code"], "AccessDenied")
        self.assertEqual(safe["http_status"], 403)
        self.assertNotIn("private provider detail", str(safe))


class ExportStorageConfigurationDiagnosticsTests(unittest.TestCase):
    def test_diagnostics_identify_selected_r2_alias_without_exposing_secrets(self):
        from storage_acceptance import _export_storage_config_diagnostics
        env = {
            "R2_ACCESS_KEY_ID": "old-export-key-xyz1",
            "R2_SECRET_ACCESS_KEY": "old-export-secret",
            "R2_ENDPOINT_URL": "https://wrong-account.r2.cloudflarestorage.com",
            "R2_BUCKET_NAME": "think-tank-private-exports",
            "R2_REGION": "eu-central-1",
            "DATA_EXPORT_AWS_ACCESS_KEY_ID": "active-export-key-b206",
            "DATA_EXPORT_AWS_SECRET_ACCESS_KEY": "active-export-secret",
            "DATA_EXPORT_AWS_ENDPOINT_URL_S3": "https://b8d5a16d7a33f342f0b790bdf8717e07.r2.cloudflarestorage.com",
            "DATA_EXPORT_STORAGE_BUCKET": "think-tank-private-exports",
            "DATA_EXPORT_AWS_REGION": "eu-central-1",
        }
        with patch.dict(os.environ, env, clear=True):
            result = _export_storage_config_diagnostics()
        self.assertEqual(result["diagnostic_version"], 2)
        self.assertEqual(result["access_key_source"], "DATA_EXPORT_AWS_ACCESS_KEY_ID")
        self.assertEqual(result["access_key_id_suffix"], "b206")
        self.assertTrue(result["access_key_aliases_conflict"])
        self.assertTrue(result["secret_key_aliases_conflict"])
        self.assertEqual(result["endpoint_account_id"], "b8d5a16d7a33f342f0b790bdf8717e07")
        self.assertEqual(result["region"], "auto")
        self.assertNotIn("active-export-secret", str(result))


class R2RawUnsignedHttpProbeTests(unittest.TestCase):
    def test_bare_http_probe_accepts_only_401_or_403_as_denial(self):
        import io
        from urllib.error import HTTPError
        from storage_acceptance import _unsigned_http_denied

        for status in (401, 403):
            error = HTTPError(
                "https://account.r2.cloudflarestorage.com/private/key",
                status,
                "Denied",
                {},
                io.BytesIO(b"<Error><Code>AccessDenied</Code></Error>"),
            )
            with patch("urllib.request.urlopen", side_effect=error):
                self.assertTrue(_unsigned_http_denied(
                    "https://account.r2.cloudflarestorage.com", "private", "key"
                ))

    def test_bare_http_probe_preserves_unexpected_provider_error(self):
        import io
        from urllib.error import HTTPError
        from storage_acceptance import _unsigned_http_denied, _step, _safe_failure, StorageProbeStepError

        error = HTTPError(
            "https://account.r2.cloudflarestorage.com/private/key",
            400,
            "Bad Request",
            {"x-amz-request-id": "request-123"},
            io.BytesIO(b"<Error><Code>InvalidArgument</Code><Message>Authorization</Message></Error>"),
        )
        with patch("urllib.request.urlopen", side_effect=error) as opened:
            with self.assertRaises(StorageProbeStepError) as caught:
                _step("r2_unsigned_access", lambda: _unsigned_http_denied(
                    "https://account.r2.cloudflarestorage.com", "private", "key"
                ))
        safe = _safe_failure(caught.exception, "r2_unsigned_access")
        self.assertEqual(safe["provider_code"], "InvalidArgument")
        self.assertEqual(safe["provider_message"], "Authorization")
        self.assertEqual(safe["provider_operation"], "GetObject")
        self.assertEqual(safe["http_status"], 400)
        self.assertEqual(safe["provider_request_id"], "request-123")
        request = opened.call_args.args[0]
        self.assertNotIn("Authorization", request.headers)

    def test_bare_http_probe_rejects_successful_anonymous_read(self):
        from unittest.mock import Mock
        from storage_acceptance import _unsigned_http_denied, StorageAcceptanceError

        response = Mock()
        response.status = 200
        response.__enter__ = lambda value: value
        response.__exit__ = Mock(return_value=False)
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(StorageAcceptanceError):
                _unsigned_http_denied(
                    "https://account.r2.cloudflarestorage.com", "private", "key"
                )


class UnsignedProbeRegressionTests(unittest.TestCase):
    def test_unsigned_probe_uses_botocore_unsigned_constant(self):
        """A plain "unsigned" string raises UnknownSignatureVersionError; botocore.UNSIGNED is required."""
        import storage_acceptance
        from botocore import UNSIGNED
        from botocore.exceptions import ClientError
        denied = ClientError(
            {"Error": {"Code": "AccessDenied"}, "ResponseMetadata": {"HTTPStatusCode": 403}}, "GetObject")
        with patch("boto3.client") as factory:
            factory.return_value.get_object.side_effect = denied
            self.assertTrue(storage_acceptance._unsigned_denied("https://s3.example.test", "eu-central-1", "bucket", "key"))
        self.assertIs(factory.call_args.kwargs["config"].signature_version, UNSIGNED)


if __name__ == "__main__":
    unittest.main()
