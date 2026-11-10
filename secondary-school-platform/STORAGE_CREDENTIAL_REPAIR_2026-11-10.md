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