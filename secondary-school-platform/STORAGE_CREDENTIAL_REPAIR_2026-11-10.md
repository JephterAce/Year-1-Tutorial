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

## Required final acceptance

The owner-protected staging diagnostic must now be run once by an authenticated owner in the Operations page:

https://learnwise-staging-api.onrender.com/admin/operations

The previous run's database-backed rate-limit window began at 2026-11-10 13:05:35 UTC. Wait until after **2026-11-10 13:20:35 UTC (14:20:35 WAT)** before running again.

A complete pass requires, independently for audio and exports:

- upload succeeds;
- authenticated retrieval succeeds;
- retrieved checksum matches;
- unsigned access is denied;
- object deletion succeeds.

Do not mark storage complete from deployment health alone. The latest post-fix PUT/GET/checksum/unsigned-denial/DELETE acceptance has not yet been run. After the owner runs it, inspect the new audit event and confirm every check above before revoking the old Neon credential.

## Safety boundaries

- Staging only. No production changes, no live payments, no public bucket exposure.
- Keep PR #1 draft/open/unmerged.
- Keep Render auto-deploy OFF.
- Never paste, print, commit or place any credential secret in chat or source control.
