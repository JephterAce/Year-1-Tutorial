# Think Tank — Storage Credential Repair
Date: 2026-11-10
Environment: Render staging only
Branch: secondary-school-platform-foundation

## Findings

The staging storage diagnostic exposed two independent credential-pair errors.

### Private audio (Neon Object Storage)

- Audio bucket: `learnwise-private-audio` (private).
- Storage endpoint and region remain the Neon staging values:
  - endpoint: `https://br-still-cherry-baz7g5hk.storage.c-8.eu-central-1.aws.neon.tech`
  - region: `eu-central-1`
  - path-style addressing: enabled.
- The previous `AWS_ACCESS_KEY_ID` selected by the app was actually the Cloudflare audio token ID (suffix `4b96`), not a Neon branch credential. Neon correctly returned `403 InvalidAccessKeyId`.
- Cleared the two `AUDIO_STORAGE_*` credential overrides so the adapter falls back to the standard Neon `AWS_*` variables.
- Created a branch-scoped Neon storage credential named `learnwise-render-staging-storage-v2`, with `storage:read` and `storage:write` scopes. Rotated this credential in place and wrote its matching `token_id` and `s3_secret_access_key` into Render:
  - safe Access Key ID suffix: `915cdc`
  - no secret values are recorded here.
- The audio adapter remains unchanged; no production or public-bucket changes were made.

### Private export storage (Cloudflare R2)

- Export bucket: `think-tank-private-exports` (private).
- Account endpoint: `https://b8d5a16d7a33f342f0b790bdf8717e07.r2.cloudflarestorage.com`
- Region: `auto`.
- The selected Access Key ID correctly matched the active Cloudflare export token (suffix `b206`), but the stored secret did not match the token value, producing `403 SignatureDoesNotMatch`.
- Rolled the existing Cloudflare export account token while preserving its bucket-scoped policy.
- Derived the S3 Secret Access Key as SHA-256 of the newly returned token value, per Cloudflare's R2 API-token documentation, and wrote that digest to `DATA_EXPORT_AWS_SECRET_ACCESS_KEY`.
- The Access Key ID, bucket, endpoint, region and bucket-scoped permissions were not changed.

## Render staging deployments

Service: `learnwise-staging-api`
URL: https://learnwise-staging-api.onrender.com
Service ID: `srv-dbkqcmt9fdbs73c2kdpg`
Workspace ID: `tea-da2svh0ae00c73cs4qq0`

1. Neon credential deploy: `dep-dbphfhmgekts739vjsqg` — LIVE.
2. Cloudflare export secret deploy: `dep-dbphfsrm8hqs73duc8kg` — LIVE.
3. Latest deployed application commit remains `c293147792a97a3848e2eae00533332a9136b037`.
4. Application health endpoint verified after deployment: `/health` returned `status=ok`, `mode=database`.
5. Render auto-deploy remains OFF.

Environment variable values are never stored in this document.

## Credential hygiene

- An unused temporary Neon credential `learnwise-render-staging-storage-v3` (suffix `09758b`) was revoked.
- The older `learnwise-render-staging-storage` credential remains active but is no longer configured in Render. Keep it until the new storage acceptance test passes; then revoke it if no other staging consumer uses it.
- Do not revoke the active `learnwise-render-staging-storage-v2` credential or roll the Cloudflare export token again unless a new diagnostic proves a need.

## Latest post-repair acceptance evidence

The newest owner-triggered staging run is recorded in Neon `audit_events` as event `159`, at **2026-11-10 13:24:07 UTC (14:24:07 WAT)**. This supersedes the older failing JSON payload that showed the pre-repair upload errors.

### Audio result: PASS

The audit record confirms all five audio checks were true:

- upload;
- authenticated retrieval;
- checksum match;
- unsigned access denied;
- deletion verified.

The selected credential fingerprint ended in `5cdc`, matching the active Neon v2 credential. No Neon key rotation is required.

### R2 result: INCOMPLETE — anonymous-access probe

The newest R2 failure is at `r2_unsigned_access`, with provider code `InvalidArgument` and HTTP `400`. It is no longer failing at `r2_upload` with `SignatureDoesNotMatch`.

The code's R2 probe order is authenticated upload, authenticated retrieval, checksum validation, unsigned retrieval, then deletion in a `finally` block. The audit event does not retain intermediate success flags when an exception occurs, so it does not independently record the first three booleans. A subsequent Cloudflare listing showed **zero objects** under the synthetic `qa-acceptance/` prefix.

The Cloudflare control plane was checked read-only after this run:

- R2 managed `r2.dev` access: `enabled=false`.
- Custom domains attached to this bucket: none.
- Bucket: `think-tank-private-exports`, jurisdiction `default`.
- Active export token remains scoped to this bucket with `Workers R2 Storage Bucket Item Write` permission.

Cloudflare's current R2 error-code reference documents missing/invalid S3 credentials as `401 Unauthorized` and insufficient permissions as `403 AccessDenied`. It does **not** document `400 InvalidArgument` as an authentication-denial result:
https://developers.cloudflare.com/r2/api/error-codes/

Cloudflare documents that R2 buckets are private by default and that public access requires explicitly enabling either a managed `r2.dev` URL or a custom domain:
https://developers.cloudflare.com/r2/buckets/public-buckets/

The control-plane settings currently verify that this bucket has no configured public route. Nevertheless, do **not** treat the unexplained `400 InvalidArgument` as a successful runtime unsigned-access check. Keep the R2 acceptance gate open until the unsigned probe's behavior is understood and the owner-triggered diagnostic records all five R2 checks as true. Do not rotate the R2 token on this evidence.

## Next action

Investigate why the anonymous S3 `GetObject` probe returns `400 InvalidArgument` for the R2 endpoint. Preserve the current working R2 credential pair and keep the independent Cloudflare public-access settings private. After a code/configuration correction is independently verified, run the owner-protected diagnostic again at:

https://learnwise-staging-api.onrender.com/admin/operations

The latest audit event was recorded at 13:24:07 UTC; the 15-minute diagnostic cooldown therefore expires after **2026-11-10 13:39:07 UTC (14:39:07 WAT)**. Do not repeatedly run the diagnostic during the cooldown.

A complete pass requires, independently for audio and exports:

- upload succeeds;
- authenticated retrieval succeeds;
- retrieved checksum matches;
- unsigned access is denied;
- object deletion succeeds.

Do not mark storage complete from deployment health or control-plane privacy settings alone.

## Safety boundaries

- Staging only. No production changes, no live payments, no public bucket exposure.
- Keep PR #1 draft/open/unmerged.
- Keep Render auto-deploy OFF.
- Never paste, print, commit or place any credential secret in chat or source control.


## Follow-up diagnostic instrumentation — 2026-11-10

To identify the exact reason for the R2 anonymous `GetObject` rejection without changing the acceptance criteria or credentials, the staging diagnostic now retains a small, sanitized set of provider error details:

- provider operation name (for example, `GetObject`);
- provider request ID, when returned;
- bounded provider error message, with URLs and long token-like values redacted;
- existing provider error code and HTTP status.

The error message is no longer discarded, but the raw exception, request headers, credentials, signed URLs and object payloads are never exposed. The test suite was updated to check redaction of long token-like values and preservation of a safe provider message.

Application commit: `e5b2a83aa95681a41ff67762c808e39bec9087bf`  
Test commit / branch head: `25d32f21b9ab57773a279268e92a286395b8294e`

Render staging deployment: `dep-dbpi0aom7kps73b0d770` — **LIVE**. The service booted successfully. Render auto-deploy remains `off`. No environment variables, Neon credentials, Cloudflare credentials, bucket policies or public-access settings were changed.

The GitHub workflow-run and combined-status queries returned no CI runs/statuses for this commit; therefore this deployment is **not** represented as CI-tested. The diagnostic code is limited to safe error reporting and leaves the strict acceptance rule unchanged: only HTTP 401/403 counts as a successful unsigned-access denial. A 400 remains a failure.

### Next owner action

The 15-minute cooldown from audit event 159 elapsed at 13:39:07 UTC (14:39:07 WAT). The owner may now run **one** fresh test at:

https://learnwise-staging-api.onrender.com/admin/operations

Please return the full safe JSON result. The new `provider_message`, `provider_operation`, and `provider_request_id` fields should tell us whether R2 is rejecting the anonymous request due to unsupported auth semantics, a malformed URL/path, or another specific request parameter. Do not rotate credentials or alter public bucket settings.

## Latest verified staging run — 2026-11-10 audit event 166

The latest server-side audit event is **166**, created at **2026-11-10 13:50:07.678 UTC (14:50:07.678 WAT)**. This is newer than event 159 and newer than the diagnostic-instrumentation deployment.

### Audio storage: PASS

The latest audit confirms all five audio checks passed:

- upload: true;
- authenticated retrieval: true;
- checksum match: true;
- unsigned access denied: true;
- deletion: true.

The selected Neon access-key suffix is `5cdc`, matching the active `learnwise-render-staging-storage-v2` credential. Neon v2 remains active with `storage:read` and `storage:write` scopes. No Neon credential rotation is needed.

### Cloudflare R2: authenticated path advances; anonymous check remains unresolved

The latest audit reaches `r2_unsigned_access` and returns:

- operation: `GetObject`;
- HTTP status: `400`;
- provider code: `InvalidArgument`;
- provider message: `Authorization`;
- provider request ID: not returned in the audit record.

The acceptance code executes authenticated upload, authenticated retrieval, checksum validation, then the unsigned read. Therefore, the run has passed the authenticated R2 upload/retrieval/checksum stages before it fails at the anonymous read. Its `finally` cleanup executes; an independent control-plane listing confirms the `qa-acceptance/` prefix is empty.

The selected R2 access-key suffix remains `b206`, endpoint account ID and bucket match the intended export configuration, and region is `auto`. This is not evidence that the R2 access key or secret needs rotation.

### Independent Cloudflare control-plane verification

Read-only checks on the same bucket confirm:

- bucket: `think-tank-private-exports`;
- managed `r2.dev` public access: `enabled=false`;
- custom domains: none configured;
- `qa-acceptance/` object count: zero.

No credentials, bucket permissions, public-access settings, or production resources were changed.

Cloudflare's current R2 error-code reference lists missing/invalid credentials as HTTP 401 `Unauthorized`, insufficient permissions as HTTP 403 `AccessDenied`, and signature mismatch as HTTP 403 `SignatureDoesNotMatch`. It does not document this HTTP 400 `InvalidArgument` / `Authorization` response as an authentication-denial result:
https://developers.cloudflare.com/r2/api/error-codes/

Cloudflare recommends presigned URLs when granting anonymous users access to private objects:
https://developers.cloudflare.com/r2/examples/authenticate-r2-auth-tokens/

### Reconciliation and next diagnostic

The operator-submitted JSON showing audio `InvalidAccessKeyId` and R2 `SignatureDoesNotMatch` does not match audit event 166 or the deployed diagnostic-v2 fields. Treat that JSON as an earlier/stale result. Use audit event 166 as the current server-side evidence.

Do not weaken the acceptance rule: only HTTP 401 or 403 counts as a successful unsigned-access denial. Do not rotate the active Neon or Cloudflare credentials, change R2 bucket permissions, enable a public route, or use a presigned URL as a substitute for this test. Keep the R2 acceptance gate open while investigating why an unsigned S3 `GetObject` is being rejected as HTTP 400 `InvalidArgument` with message `Authorization`.

The latest deployed diagnostic remains staging-only; Render auto-deploy is OFF, production is untouched, and PR #1 remains draft/open/unmerged.


## Raw unsigned R2 request probe — CI and staging deployment

To distinguish SDK-specific request handling from the R2 endpoint's treatment of an anonymous request, the staging diagnostic now uses a plain Python HTTPS GET for the R2 unsigned-access step. It sends no `Authorization` header and does not use SigV4. The response parser reads at most 4 KB of XML and retains only the bounded safe provider code, message, request ID and operation.

The rule remains strict:

- HTTP 401 or 403: anonymous access denied (pass);
- HTTP 2xx: private object exposed (fail);
- all other HTTP responses, including 400: fail with safe diagnostic details.

The audio test path is unchanged. R2 credentials, permissions, endpoint, bucket settings and public-access configuration are unchanged.

### Verification

- Full GitHub Actions PR workflow on branch head `d1fc658479cd49dc5b96312c6a9f4539bce99c17`: **success** (run 42830156978).
  - unit and security tests: success;
  - Python/frontend/script syntax checks: success;
  - PostgreSQL migrations and guarded backup/restore rehearsals: success;
  - PostgreSQL schema, synthetic identity, payment end-to-end and student-journey tests: success;
  - anonymous and authenticated browser acceptance against disposable PostgreSQL fixtures: success;
  - container build: success;
  - staging health check: success.
- Separate read-only browser acceptance workflow: success (run 42830144711).
- Render staging deployment `dep-dbpiae8n74is73e2627g`: **LIVE**, deployed commit `d1fc658479cd49dc5b96312c6a9f4539bce99c17`, finished `2026-11-10 14:08:23.993 UTC`.
- Render service is still on `secondary-school-platform-foundation`; auto-deploy remains OFF.
- PR #1 remains open, draft and unmerged.

### Next owner action

The latest previous storage audit event 166 was recorded at 13:50:07.678 UTC (14:50:07.678 WAT). Its 15-minute cooldown elapsed at 14:05:07.678 UTC (15:05:07.678 WAT). The new diagnostic is now live, so the owner may run **one** fresh storage acceptance at:

https://learnwise-staging-api.onrender.com/admin/operations

Share the full safe JSON result. For R2, check the latest `r2_exports` result's `failure_phase`, `provider_code`, `provider_message`, `provider_request_id`, and `http_status`. Audit the latest `audit_events` entry after the run and verify the `qa-acceptance/` prefix is empty. The R2 gate remains open unless all five checks pass, including a 401/403 result from this raw unsigned request.
