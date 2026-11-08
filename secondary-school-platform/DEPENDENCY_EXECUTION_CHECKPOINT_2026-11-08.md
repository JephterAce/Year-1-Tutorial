# Dependency execution checkpoint — 8 November 2026

## Scope and safety

This checkpoint records an attempted execution of the remaining provider, people/approval and operational dependencies for Think Tank staging. Work remained on `secondary-school-platform-foundation`. No production deployment, PR merge, main-branch change, live payment, credential disclosure, or student onboarding was performed.

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
- `DATA_EXPORT_WORKER_ENABLED` (must remain false until approvals and storage controls are verified)

### Cloudflare R2 — partial completion, 8 November 2026

The owner confirmed R2 activation in the Cloudflare Dashboard. The connected Cloudflare account is `b8d5a16d7a33f342f0b790bdf8717e07`.

Created bucket:
- Name: `think-tank-private-exports`
- Bucket ID: `09ee0a4e92a445889e76a1ca94db79a3`
- Location: `WEUR` (Western Europe)
- Storage class: `Standard`
- Jurisdiction: `default`

Read-after-create verification succeeded. The bucket's managed `r2.dev` public domain is explicitly disabled (`enabled=false`). A CORS policy does not exist; this is intentional for the current server-to-server design and should not be opened to browser origins without a reviewed requirement. No public custom domain was attached.

Render service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) was updated with non-secret configuration only:
- `DATA_EXPORT_STORAGE_BUCKET=think-tank-private-exports`
- `DATA_EXPORT_AWS_ENDPOINT_URL_S3=https://b8d5a16d7a33f342f0b790bdf8717e07.r2.cloudflarestorage.com`
- `DATA_EXPORT_AWS_REGION=auto`
- `DATA_EXPORT_WORKER_ENABLED=false`

The Render environment update triggered staging deployment `dep-dbo3ahrm8hqs73fenfhg` from commit `77a7589ee76336b339a66c687526221b48d56eec`; its latest observed state at checkpoint preparation was `update_in_progress`. Verify final deployment status and staging health before treating configuration as active.

### Credential and object-test blockers

The Cloudflare connector is authenticated through OAuth and its API connection does not have the `API Tokens Read/Write` scopes required to create an R2 S3 API token programmatically. The token permission-groups API returned 403 / error 9109. No S3 access key or secret was created, exposed, or stored.

Owner action required in Cloudflare Dashboard:
1. Open R2 Object Storage → Overview → Manage R2 API Tokens.
2. Create an R2 API token with **Object Read & Write** permissions, scoped only to `think-tank-private-exports`. Do not grant Admin Read/Write or all-bucket access.
3. Copy the Access Key ID and Secret Access Key once; never paste them into chat or GitHub.
4. In Render → `learnwise-staging-api` → Environment, set:
   - `DATA_EXPORT_AWS_ACCESS_KEY_ID`
   - `DATA_EXPORT_AWS_SECRET_ACCESS_KEY`
   Enter the values directly into Render's secret environment fields.

After the owner has added the two secrets, perform an isolated synthetic-object test using the exact application credentials: upload a random test object, retrieve and compare its bytes/checksum, verify an unauthenticated request is denied, verify a credential scoped to another bucket cannot read/write this bucket if a separate test credential is available, then delete the test object. Do not use learner records or personal data. Do not enable the export worker during this test.

**Current disposition:** bucket created and public access disabled; non-secret Render configuration submitted; dedicated bucket-scoped S3 credentials and object-level acceptance tests remain outstanding. Keep `DATA_EXPORT_WORKER_ENABLED=false`.

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
| Export storage | R2 bucket created; public domain disabled; non-secret Render config submitted; bucket-scoped S3 token and object tests outstanding |
| Second administrator | Not appointed; one active admin |
| Subject teachers | Not appointed; 18 mappings remain unapproved |
| Nigerian counsel | Not appointed; legal review outstanding |
| Safeguarding lead | Not appointed; guardian/child-safety approvals outstanding |
| Independent security reviewer | Not appointed; assessment not performed |
| Managed recovery | 6-hour history window; no snapshots/schedule; backup branch endpoint unavailable; restore drill outstanding |
| Monitoring | Default notification setting; no named recipient or delivery test |

## Release restriction

Do not enable exports, schedule an export worker, process real learner data, publish curriculum, activate live payments, deploy to production or merge PR #1 until the relevant technical tests, external evidence and owner approvals are recorded.


## Follow-up verification — 8 November 2026, 09:39 WAT

The Render environment update completed successfully. Deployment `dep-dbo3ahrm8hqs73fenfhg` reached status `live` on the staging service, using the existing docs checkpoint commit `77a7589ee76336b339a66c687526221b48d56eec`. The deployment was triggered by the environment-variable update. This confirms Render accepted the non-secret export configuration; it does not prove S3 authentication or object operations.

A direct external health check could not be completed through the available connected tools in this run. Do not mark post-deploy health as re-verified based solely on the deployment status. The prior owner-reported health response remains historical evidence only.

The checkpoint file itself was then updated on `secondary-school-platform-foundation` with commit `c241717a2aff80c417a483ef0111d3f5554b2884`. Render auto-deploy is disabled, so this documentation-only commit was not deployed. No changes were made to `main`, and PR #1 remains open/unmerged.


## R2 object acceptance attempt — 8 November 2026

The owner reported that the two R2 S3 credentials have now been configured directly in Render. Secret values were not requested, read, copied, or exposed in this workflow.

### Deployment state

The staging deployment for commit `358c3ebcefff2cb689f9323f0e7bbd44cf89fd7b`, deployment `dep-dbo3d93rjlhs73aahtng`, was independently queried and returned status `live` (started 08:45:24Z; finished 08:46:02Z). The service remains `learnwise-staging-api` on branch `secondary-school-platform-foundation`; auto-deploy remains disabled. The Render service metadata interface available to this run does not expose environment-variable presence or secret values, so the owner's report is recorded as an owner assertion rather than independently verified secret configuration.

### Requested object tests — not executed

The following acceptance tests remain **NOT RUN**, not passed:
1. Upload a synthetic object to `think-tank-private-exports`.
2. Retrieve it and compare exact bytes/checksum.
3. Request the object without authentication and confirm access is denied.
4. Confirm the credential cannot access a different bucket (and, if supported, that an alternate bucket-scoped credential cannot access this bucket).
5. Delete the synthetic object and verify it is absent.

Reason: the available connected Cloudflare interface exposes account-management API requests, not authenticated S3-compatible object operations using the secret values stored inside Render. The Render interface available in this run can inspect deployment/service metadata and update environment variables, but does not provide a shell/exec facility or a way to invoke an in-container one-off test. No application test endpoint for this purpose was located in the repository search performed during this run. The external unauthenticated probe could not reach the R2 endpoint because outbound DNS resolution from the execution environment failed; therefore no HTTP denial status was observed. The R2 public `r2.dev` domain remains disabled according to the previously verified bucket configuration, but that is not a substitute for an HTTP unauthenticated-denial test against the S3 endpoint.

No test object was created, retrieved, or deleted; no bucket-boundary result is claimed. No test data or learner data was uploaded. Keep `DATA_EXPORT_WORKER_ENABLED=false` and do not treat R2 object acceptance as complete.

### Safe completion procedure

Run a one-off S3-compatible test from the staging service runtime or a trusted operator environment with the two Render-held secrets, using a newly generated random key under a dedicated test prefix. The test must: PUT a fixed synthetic byte payload; GET it and compare SHA-256 and byte length; issue an unsigned GET and require a 403/401 denial (or equivalent S3 AccessDenied); attempt a bucket-boundary operation using a credential restricted to a different test bucket, requiring denial; DELETE the test key using the intended bucket-scoped credential; and finally HEAD/GET the key to confirm absence. Capture status codes, bucket/key (non-sensitive), byte length and checksum only—never credential values or signed URLs. If a separate bucket-scoped credential is not available, mark cross-bucket isolation as not tested rather than weakening permissions or creating broad credentials. Do not enable the export worker.

### Updated disposition

R2 bucket creation and public-domain disablement: previously verified. Render deployment: verified live. Owner-reported credential configuration: acknowledged, not independently inspected. Synthetic upload/retrieval/checksum, unsigned denial, bucket isolation, and deletion: not run; remain outstanding pending an execution path that can safely use the Render-held secrets.


## Staging deployment follow-up — 8 November 2026, 09:07 WAT

The current branch head `f73f14592d9a21af803f01e6408dd06d4bb269a3` was deployed to the existing Render staging service `learnwise-staging-api` (Frankfurt, Free plan) as deployment `dep-dbo3n5hsrm7s73at12j0`.

- Render build completed successfully at 09:06:40Z.
- Render deployment completed with status `live` at 09:06:52Z.
- Render application logs show Gunicorn 23.0.0 listening on `0.0.0.0:8000`, both workers booted, and Render reported `Your service is live`.
- The service remains attached to `secondary-school-platform-foundation`; auto-deploy remains disabled.
- No production service, `main` branch, or PR merge was touched.

The latest exact-head GitHub Actions run before this deployment, `42465080496`, completed successfully on `f73f14592d9a21af803f01e6408dd06d4bb269a3`. Its three jobs passed: API/unit/security and local disposable-PostgreSQL/browser acceptance, non-publishing container build, and public staging health. The health job ran before the 09:06 deployment, so it is not post-deploy health evidence.

### Remaining immediate staging acceptance

The repository includes a separate `workflow_dispatch` workflow at `.github/workflows/think-tank-staging-browser.yml` for authenticated browser acceptance against the live staging URL. The available GitHub connector in this execution can read workflow runs and logs but does not expose a workflow-dispatch action. Therefore this workflow has not been dispatched and authenticated browser acceptance against the newly deployed Render instance remains outstanding. Do not claim it passed.

A post-deployment HTTP health check also remains to be repeated after this deployment. Render deployment status and Gunicorn startup logs are positive deployment evidence, but are not substitutes for a fresh HTTP 200 / JSON `status=ok` response.

### Current staging disposition

- **Deployed:** branch head `f73f14592d9a21af803f01e6408dd06d4bb269a3`, deployment `dep-dbo3n5hsrm7s73at12j0`, status `live`.
- **Passed:** latest exact-head CI run `42465080496` (three jobs).
- **Not yet re-verified after this deploy:** public `/health` endpoint.
- **Not run against live staging:** authenticated Playwright browser acceptance.
- **Still deferred:** R2 object-level PUT/GET/checksum, unsigned denial, bucket-boundary and deletion tests; export worker remains disabled.
- **Still release-blocking:** SMTP delivery/recovery, Paystack sandbox E2E, private audio acceptance, authorised curriculum and teacher review, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, managed backup restoration, monitoring alert delivery, second administrator and independent security review.

No learner data or live payment was used. No production launch or PR merge is authorised by this checkpoint.
