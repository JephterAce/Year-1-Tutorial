# Dependency execution checkpoint — 8 November 2026

## Scope and safety

This checkpoint records an attempted execution of the remaining provider, people/approval and operational dependencies for Think Tank staging. Work remained on `secondary-school-platform-foundation`. No production deployment, PR merge, main-branch change, live payment, paid-service activation, credential disclosure, or student onboarding was performed.

## Provider credentials and integrations

### Brevo SMTP

The application reads these Render runtime variables:
- `SMTP_HOST`
- `SMTP_PORT` (normally 587 with STARTTLS; 465 uses SMTP over SSL)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `PUBLIC_APP_URL` (must be HTTPS)

The SMTP implementation is present and mocked transport tests exist. No provider-side delivery can be confirmed without a verified Brevo sender, valid SMTP credentials and a controlled mailbox test. Credentials must be entered directly in Brevo/Render; do not place them in GitHub, logs or chat. Keep registration closed except for a controlled test.

### Paystack sandbox

The server-side verifier reads `PAYSTACK_SECRET_KEY`. Webhook signature validation is implemented, but the helper explicitly does not perform transaction/order reconciliation, entitlement fulfilment, refund processing or full event lifecycle handling by itself. CI tests use synthetic/mocked provider responses. No real sandbox charge, webhook delivery/retry, refund or reconciliation evidence exists. Add the sandbox key only in Render secrets and run an owner-authorised controlled sandbox test. Live payments remain disabled.

## Private storage and credentials

### Current Neon storage credential

Neon staging branch: `think-tank-staging` (`br-still-cherry-baz7g5hk`).

Credential metadata confirms an existing credential named `learnwise-render-staging-storage` with `storage:read` and `storage:write` capabilities, anchored to the staging branch. These Neon capabilities are branch-scoped, not individual-bucket scoped. A new credential was not issued because it would not improve the scope boundary. Do not reuse this broad branch capability for exports without an explicit security decision.

Audio storage code reads:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ENDPOINT_URL_S3`
- `AWS_REGION`
- `AUDIO_STORAGE_BUCKET`

The export worker uses a separate namespace:
- `DATA_EXPORT_STORAGE_BUCKET`
- `DATA_EXPORT_AWS_ENDPOINT_URL_S3`
- `DATA_EXPORT_AWS_REGION`
- `DATA_EXPORT_AWS_ACCESS_KEY_ID`
- `DATA_EXPORT_AWS_SECRET_ACCESS_KEY`
- `DATA_EXPORT_WORKER_ENABLED` (currently configured to remain false until approvals and storage controls are verified)

### Cloudflare R2 attempt

The connected Cloudflare account returned HTTP 403 / error 10042: R2 must first be enabled through the Cloudflare Dashboard. Cloudflare's R2 token documentation also states R2 must be purchased/activated before API token creation. No R2 bucket or token was created, and no billing or paid-service activation was initiated.

**Decision required:** either (a) owner activates R2 and creates a token scoped to the exact private bucket with only the required object read/write permissions, or (b) owner explicitly accepts the Neon branch-wide storage capability after security review. Keep export worker disabled until a second authorised administrator and retention controls are in place.

## People and formal approvals

These cannot be completed by software automation or inferred:
- second authorised administrator for two-person export approval;
- qualified subject teachers to review the 18 SS1–SS3 × six-subject mappings;
- Nigerian privacy/legal counsel;
- designated safeguarding lead and guardian-consent approval;
- independent security reviewer.

No identities or appointments were supplied, so no users were invited, admin accounts created, curriculum marked approved, or legal/safeguarding/security sign-offs fabricated. The staging database previously showed one active admin and zero curriculum topics.

## Managed backup and recovery

Read-only Neon project metadata reports:
- project `learnwise`, region `aws-eu-central-1`;
- history retention `21600` seconds (6 hours);
- staging branch snapshot schedule: empty;
- project snapshot list: empty.

The existing backup branch `think-tank-staging-backup-2026-11-08` (`br-super-haze-bazf13ia`) is listed as ready, but its database endpoint is unavailable: the read-only inspection and connection-string lookup returned endpoint-not-found errors. It is not a verified managed restore source. The repository's guarded `ops/backup_restore_rehearsal.sh` remains limited to a disposable local target and CI's local pg_dump/pg_restore pass does not prove managed PITR or backup restoration.

No automatic snapshot schedule was enabled because retention/cost and the approved RPO/RTO were not established. Required next action: owner approves recovery objectives, retention and recovery owner; provision/confirm an executable managed restore source; restore into an isolated target; validate migration history/data integrity; record actual RPO/RTO. Never restore over staging or production during a rehearsal.

## Monitoring and alert delivery

Render service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) remains on Free/Frankfurt with auto-deploy disabled. Render reports `notifyOnFail=default`; no explicit recipient or delivery test is recorded. Prior metrics returned no HTTP request/latency or CPU samples and one memory sample; no alert delivery evidence exists. No connected Render action supports setting a named alert recipient or verifying delivery.

Required next action: owner names the alert recipient/on-call contact and configures supported Render/uptime monitoring; send a controlled synthetic health/failure alert and record receipt and escalation acknowledgement. Monitor health, HTTP 5xx, deployment failures, memory/CPU, database connectivity, SMTP failures, payment outbox failures and private-media errors without logging secrets or bearer URLs.

## Current disposition

| Dependency | Outcome |
|---|---|
| Brevo SMTP | Application variable names identified; provider credentials/sender/mailbox test still required |
| Paystack sandbox | Secret variable identified; provider sandbox test still required |
| Export storage | Existing Neon credential confirmed branch-wide; bucket-level decision unresolved; R2 activation unavailable pending owner action |
| Second administrator | Not appointed; one active admin |
| Subject teachers | Not appointed; 18 mappings remain unapproved |
| Nigerian counsel | Not appointed; legal review outstanding |
| Safeguarding lead | Not appointed; guardian/child-safety approvals outstanding |
| Independent security reviewer | Not appointed; assessment not performed |
| Managed recovery | 6-hour history window; no snapshots/schedule; backup branch endpoint unavailable; restore drill outstanding |
| Monitoring | Default notification setting; no named recipient or delivery test |

## Release restriction

Do not enable exports, schedule an export worker, process real learner data, publish curriculum, activate live payments, deploy to production or merge PR #1 until the relevant technical tests, external evidence and owner approvals are recorded.
