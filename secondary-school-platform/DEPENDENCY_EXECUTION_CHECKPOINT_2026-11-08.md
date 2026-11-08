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

The staging deployment for commit `358c3ebcefff2cb689f9323f0e7bbd44cf89fd7b`, deployment `dep-dbo3d93rjlhs73aahtng`, was independently queried and returned status `live` (started 08:45:24Z; finished 08:46:02Z). The Render service remains `learnwise-staging-api` on branch `secondary-school-platform-foundation`; auto-deploy remains disabled. The Render service metadata interface available to this run does not expose environment-variable presence or secret values, so the owner's report is recorded as an owner assertion rather than independently verified secret configuration.

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


## Post-deployment acceptance confirmation — 8 November 2026, 09:09 WAT

The post-deployment public health check was subsequently completed by GitHub Actions run `42465816566` on branch head `a19214d647478b37702fb52e336fc8a3638f05bb`, after Render deployment `dep-dbo3n5hsrm7s73at12j0` had reached `live`.

Observed from the health job log:
- HTTP status: `200`
- JSON `status`: `ok`
- JSON `mode`: `database`
- JSON `service`: `secondary-school-api`

All three jobs in run `42465816566` completed successfully:
- `staging-health`
- `container-build`
- `api-tests`, including unit/security tests, migration rehearsal, disposable local backup/restore rehearsal, PostgreSQL integration/E2E/student journey and anonymous/authenticated Playwright acceptance on disposable fixtures.

This confirms the deployed staging endpoint is healthy after the deployment. The browser tests in this workflow ran against disposable CI fixtures, not the live Render service. The separate manually dispatched staging browser workflow remains outstanding.

A read-only Neon query on staging branch `think-tank-staging` confirmed 20 migration-history rows, 1 admin user, 0 students, 6 subjects, 0 topics and 6 audit events. The staging branch and the pre-migration backup branch both report Neon state `ready`; this metadata does not constitute a managed restore drill.

No other release restrictions are lifted. R2 object tests remain deferred/not run; export worker remains disabled; provider, curriculum, legal, safeguarding, managed-recovery, monitoring, second-admin and independent-security gates remain open.


## Safe live-staging browser workflow adjustment — 8 November 2026

The dedicated manual staging browser workflow `.github/workflows/think-tank-staging-browser.yml` was reviewed before execution. Its previous `npm test` command ran both read-only anonymous checks and authenticated write tests. The authenticated tests create and publish an assessment, queue/cancel an export request, and submit/withdraw a student privacy request. They are not appropriate for the live staging database, which currently has one administrator and zero students.

The workflow was therefore changed in commit `3d5ee6d61ec197cc12ebdf13bf34391911e18efe` to run only `staging.spec.js` against the live staging URL. This suite checks public health, student-facing page delivery, registration/recovery form presence, mobile layout, and anonymous access denial; it does not submit registrations, payments, exports or privacy requests. The authenticated suite remains reserved for isolated disposable fixtures.

The current GitHub connector exposes workflow/run reads and reruns but no `workflow_dispatch` action. Therefore the revised live-staging browser workflow has **not yet been dispatched**. The workflow file is committed on `secondary-school-platform-foundation`; it must be manually started from GitHub Actions. No live service data was changed by this adjustment. Render auto-deploy remains disabled, so this workflow-only commit has not been deployed to Render.

The latest application deployment remains `dep-dbo3n5hsrm7s73at12j0` on application commit `a19214d647478b37702fb52e336fc8a3638f05bb` (the Render deployment was built from that application code; subsequent commits are documentation/workflow-only). The post-deployment health job in run `42465816566` passed HTTP 200 with JSON `status=ok`, `mode=database`, `service=secondary-school-api`.

Release restrictions remain unchanged: no public onboarding or production launch. SMTP/recovery, Paystack sandbox, real private audio, licensed curriculum and teacher approval, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, managed recovery, monitoring alert delivery, second administrator, independent security review and R2 object acceptance remain outstanding.


## Deployment SHA clarification — 8 November 2026

For avoidance of ambiguity: Render deployment `dep-dbo3n5hsrm7s73at12j0` was built from Git commit `f73f14592d9a21af803f01e6408dd06d4bb269a3` (Render's deployment record confirms this). GitHub Actions run `42465816566` later tested branch head `a19214d647478b37702fb52e336fc8a3638f05bb`, and its post-deployment health job passed, but that does **not** mean Render deployed `a19214d`. Subsequent commits `20836ee`, `3d5ee6d` and `7bbdbff` are checkpoint/workflow documentation or workflow-only changes; Render auto-deploy is disabled, so they were not deployed. The currently live Render deployment remains `dep-dbo3n5hsrm7s73at12j0` on `f73f145`.


## Verification continuation — 8 November 2026, 09:12 WAT

### Exact-head GitHub checks

The latest branch head at the time of this verification was `1b3463fbf381ba9917a01aeeb45c6d8ad085bb71`. Both the push workflow `42466020956` and PR workflow `42466026453` completed successfully on this exact head. Each run passed all three jobs:
- `api-tests`: unit/security tests, Python/JavaScript/operations-script syntax, disposable PostgreSQL migration replay, local backup/restore rehearsal, schema integration, assessment/payment E2E, registration-to-results student journey, and anonymous/authenticated Playwright acceptance against disposable fixtures.
- `container-build`: application container built without publishing.
- `staging-health`: public staging health assertion completed successfully.

The push run's health job log explicitly records HTTP 200 and JSON `status='ok'`, `mode='database'`, `service='secondary-school-api'` from `https://learnwise-staging-api.onrender.com/health`. This is a fresh post-deployment health check on 8 November at 09:10:14Z. It does not mean the latest GitHub documentation commit was deployed to Render.

Run links:
- Push: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42466020956
- PR: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42466026453

### Live staging browser workflow

The revised workflow file `.github/workflows/think-tank-staging-browser.yml` remains read-only and runs only `staging.spec.js`. A read of the latest workflow-run collection did not return a run for this workflow; no completed live-staging browser acceptance result is available to record. The GitHub connector still does not expose a workflow-dispatch operation. Do not infer that the workflow passed from the owner's confirmation that the Run workflow action was tapped; a completed run ID and job result are required.

### Render operational signals

Render event history confirms the latest staging deployment `dep-dbo3n5hsrm7s73at12j0` completed successfully at 09:06:52Z, and the build completed at 09:06:40Z. Startup logs show Gunicorn 23.0.0 listening on port 8000, workers booted, and Render's `Your service is live` message. No failure event was present in the returned recent event page.

The metrics query returned CPU and memory samples, but no HTTP request-count, HTTP-latency or instance-count series in the queried interval. CPU and memory values are not sufficient to establish traffic or alert delivery. The Render service remains on Free/Frankfurt with auto-deploy disabled. Monitoring alert recipient and delivery test remain unverified.

### Managed recovery state

A fresh read-only Neon query confirms:
- staging branch `think-tank-staging` is `ready`;
- backup branch `think-tank-staging-backup-2026-11-08` is `ready`;
- migration rehearsal branches remain present and `ready`;
- project snapshot list is empty;
- staging branch automatic snapshot schedule is empty.

A ready Neon branch is not a completed backup restore drill. No snapshot schedule was enabled because retention/cost and approved RPO/RTO remain undecided. Managed restore and recovery sign-off remain outstanding.

### Release posture

No production deployment, PR merge, main-branch change, live payment, export worker activation or learner-data processing occurred. PR #1 remains open/draft/unmerged. Public student onboarding remains blocked by the external gates already recorded above.


## Continuation — latest branch and staging verification, 8 November 2026

### Current GitHub branch and checks

The development branch head is `a21f73a97c7f29313f9bebf31b9b4af7bfe5f746`. The automatic push and pull-request CI runs on this exact commit both completed successfully:
- Push run: `42466299588` — all three jobs passed (`api-tests`, `container-build`, `staging-health`).
- PR run: `42466302891` — all three jobs passed.

The push run's staging-health job completed successfully against the configured Render health URL. Earlier health job logs explicitly captured HTTP 200 and JSON `status=ok`, `mode=database`, `service=secondary-school-api` at 09:10:14Z. The current GitHub API confirms the latest exact-head health job passed, but its detailed response body was not separately retrieved in this verification.

### Render staging deployment and configuration

A fresh Render service read confirms:
- Service: `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`)
- URL: `https://learnwise-staging-api.onrender.com`
- Branch: `secondary-school-platform-foundation`
- Region: Frankfurt; plan: Free; one instance
- Auto-deploy: disabled
- Failure notifications: `default` (no named alert recipient/delivery evidence)
- Latest deployment: `dep-dbo3n5hsrm7s73at12j0`, status `live`, application commit `f73f14592d9a21af803f01e6408dd06d4bb269a3`

Render event history shows the latest build and deployment both succeeded. The currently live application deployment is still `f73f145`; the later GitHub commits are checkpoint/workflow changes and are not deployed. No code deployment was triggered because no application-code change was made and auto-deploy is intentionally disabled.

### Live-staging browser workflow dispatch

The revised workflow `.github/workflows/think-tank-staging-browser.yml` is read-only and is intended to run `staging.spec.js` only. The latest returned GitHub Actions run collection contains only the normal `secondary-school-platform.yml` push/PR workflows; it does not show a completed run of the dedicated browser workflow. The connected GitHub tool set exposes workflow-run reads and reruns, but no `workflow_dispatch` action. Therefore live-staging browser acceptance remains **not verified**. No claim of completion is made.

### Release posture unchanged

PR #1 remains open, draft and unmerged; base branch `main` remains unchanged. No production deploy, live payment, export worker activation, learner-data processing or public student onboarding occurred. Provider tests, private audio acceptance, curriculum licensing/teacher review, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, second administrator, managed restore drill, monitoring alert delivery, independent security review, and R2 object-level tests remain open. Do not enable exports or launch publicly until the corresponding evidence and approvals exist.


## Owner-reported live-staging browser workflow result — 8 November 2026

The owner reports that the manually dispatched workflow `.github/workflows/think-tank-staging-browser.yml` completed with a green success indicator in GitHub Actions. On that basis, the live-staging browser workflow is recorded as **owner-reported passed**. The workflow is configured to run the read-only `staging.spec.js` suite only (public health, student-facing page, registration/recovery form presence, mobile layout and anonymous access denial); it does not perform authenticated write operations.

The connected GitHub interface available for this checkpoint does not expose the workflow-dispatch run identifier or its job logs, so the green result has not been independently matched to a run ID or individual test output. Retain this distinction in audit records. This result does not close the separate SMTP/recovery, Paystack sandbox, private audio, R2 object, managed recovery, monitoring, curriculum, safeguarding, legal, second-administrator or independent-security gates.


## Student account and password-reset investigation — 8 November 2026

### Frontend inspection

Inspected the complete `secondary-school-platform/frontend/account.html` on `secondary-school-platform-foundation`.

- The page has a student registration form, sign-in form and password-reset request form.
- The reset form has a submit handler for `POST /api/v1/auth/password-reset`.
- On a successful HTTP response, it displays the server's generic confirmation message in `#resetMsg`.
- On a failed HTTP request, it also displays a generic confirmation message, deliberately avoiding account-existence disclosure.
- The API helper sends JSON to the same origin (unless `learnwise-api-base` is populated) and includes same-origin credentials.
- The handler is present; source inspection does not prove that the deployed browser received this exact page/script or that a live browser request completed.

### Backend inspection

The Flask route `POST /api/v1/auth/password-reset` calls `request_password_reset(email)`. It sends a reset email only when that function returns a token and the associated student email can be retrieved. Exceptions are logged server-side, but the client still receives HTTP 202 with the same generic message.

The earlier read-only Neon staging query reported **zero student accounts** and one administrator. Therefore, for the email address used in the attempted reset, no reset message should be sent unless a corresponding eligible student account exists. The generic response is intentional and does not prove SMTP delivery.

The registration route is explicitly gated by `STUDENT_REGISTRATION_ENABLED`; when disabled it returns HTTP 503 with `registration_temporarily_disabled`. Do not enable public registration merely to create a test account.

### Existing automated coverage

Inspected `secondary-school-platform/backend/test_identity_routes.py`. It contains a mocked test asserting that a password-reset request for an unknown account returns HTTP 202 and the generic message. It also tests registration's consent requirement and a mocked verification-email call. The file's tests use mocks; they do not establish a live Brevo SMTP connection, real mailbox delivery, or live browser feedback. No test run was initiated as part of this source inspection.

### Finding and disposition

- **Correct student-facing interface:** confirmed from source.
- **Registration blocked:** confirmed by backend feature-flag gate; this is intentional.
- **Reset handler present:** confirmed in source.
- **Reset email delivered:** not verified; with zero student accounts, no email is expected for an unknown address.
- **Brevo SMTP credentials and sender:** owner previously reported the six environment-variable names exist and the sender address is verified; actual secret values and delivery remain unverified.
- **Live browser click/response:** not independently verified. The user's report that the button appeared to do nothing remains a usability/production-browser observation requiring a trace from a controlled eligible test account.
- **Public registration:** keep disabled. Do not create a student account through an alternative public interface.

### Safe next test

Use an isolated staging-only test account created through an approved administrative/test-fixture procedure, not public registration and not a real learner identity. Then submit a reset request through the actual account page, verify the generic on-page response, confirm Brevo receives the message, open the one-time link, complete password reset and sign in with the new password. Record timestamps and pass/fail outcomes without recording passwords, tokens, signed links or SMTP secrets. The available Render integration does not provide shell/exec access, and no safe administrative test-account creation action was available in this run; therefore this live test was **not performed**.

No application code, feature flags, environment variables, database rows, live accounts or production settings were changed by this investigation. PR #1 remains unmerged; `main` remains untouched.


## Controlled staging student-account provisioning review — 8 November 2026

### Existing provisioning paths

A source review of the complete Flask route table and identity modules found:
- Student creation is exposed only through `POST /api/v1/auth/register`, which is disabled in staging unless `STUDENT_REGISTRATION_ENABLED` is explicitly enabled.
- The admin API provides administrator authentication and protected review/operations functions, but no administrator-controlled student invitation or test-account provisioning endpoint was found.
- `bootstrap_admin.py` is a one-time first-owner bootstrap, requires an explicit confirmation environment variable, and refuses to run if any admin already exists. It is not a student-account tool and must not be reused.
- `identity_service.register_student` creates a pending student, stores a hashed email-verification token and consent records, and returns a one-time token for email delivery. Bypassing this flow with direct SQL would bypass the intended identity/verification path and is not an acceptable test-account method.
- No supported safe staging-only account-provisioning script or admin UI flow was located in the inspected backend routes and modules.

### Fresh read-only staging database check

On Neon project `spring-cloud-84267029`, branch `think-tank-staging` (`br-still-cherry-baz7g5hk`), database `learnwise`, using the read-only application role, a fresh query returned:
- student rows: **0**
- active administrators: **1**
- unconsumed, unexpired identity tokens: **0**

This confirms there is currently no student account against which a password-reset email could be sent, and no pending verification token.

### Decision and next implementation requirement

Do not switch on public student registration, insert a synthetic student directly with SQL, reuse the one-time admin bootstrap, or create an unaudited account.

The safe path is to implement a narrowly scoped, staging-only, admin-authenticated test-account invitation/provisioning workflow that:
1. is disabled by default and rejects non-staging environments;
2. requires an authenticated owner/admin session and CSRF protection;
3. accepts only a reserved synthetic test identity/domain and enforces a short expiry;
4. uses the existing student creation, token hashing, consent/version recording and email-delivery services rather than bypassing them;
5. creates an auditable event and supports explicit expiry/revocation/cleanup;
6. never exposes raw tokens or credentials in API responses or logs;
7. has automated tests proving the route is inaccessible in production, inaccessible anonymously, and cannot provision arbitrary real learner identities.

After review and staging deployment, use that controlled account to test Brevo verification email, account activation, login, password-reset delivery, reset completion, and subsequent login. Public registration must remain disabled throughout.

### Current result

Provisioning route/script: **not present**. Test account: **not created**. No database writes or environment changes were made. The existing live staging app remains on the previously recorded deployment; no deploy was triggered. This review does not close SMTP delivery or password-recovery acceptance.


## Owner-only staging SMTP diagnostic implementation — 8 November 2026

### Implemented on the development branch

A narrowly scoped application SMTP diagnostic has been added to the Flask backend and administrator operations page. It is intended to establish whether the staging application can submit a token-free email through its configured SMTP provider, without requiring a student account or changing public registration.

Changes on `secondary-school-platform-foundation`:
- `backend/identity_email.py`: added `send_admin_diagnostic(email)`, which sends a fixed message with no identity token, password-reset link or other bearer secret.
- `backend/admin_auth.py`: added a separate database-backed rate-limit key for SMTP diagnostics, limited to one attempt per administrator per hour. The rate-limit subject is HMAC-hashed with the existing `AUTH_RATE_LIMIT_PEPPER`.
- `backend/app.py`: added `POST /api/v1/admin/diagnostics/smtp`. It is available only when `APP_ENV=staging` and `ADMIN_SMTP_DIAGNOSTIC_ENABLED` is explicitly enabled; it requires an authenticated owner session and CSRF validation; it sends only to the session's administrator email; and it records success/failure audit events without provider details or secrets.
- `admin/operations.html`: added an owner-visible control to request the test message from the protected operations page.
- `backend/.env.example`: documents `ADMIN_SMTP_DIAGNOSTIC_ENABLED=false` as the default.

Automated tests were added for token-free message content, route default-off behaviour, staging-only restriction, anonymous denial, non-owner denial, owner-only recipient selection, audit invocation and the separate one-per-hour rate limit.

### Safety boundaries and current verification status

- The diagnostic flag remains **off by default**. No Render environment variable was changed.
- No SMTP message has been sent by this implementation yet.
- No SMTP credentials or values were read, copied, or exposed.
- The endpoint is not deployed to Render staging; Render auto-deploy remains disabled.
- Automated tests have been authored but their CI result is pending. Do not treat mocked SMTP tests as proof of Brevo delivery.
- Student registration remains disabled. No student account or database row was created.
- No production deployment, PR merge or change to `main` was made.

### Commits

- Rate-limit and diagnostic backend work, tests, UI and configuration were committed in sequential commits on `secondary-school-platform-foundation`; latest implementation commit before this checkpoint: `fed03a858bd1309c9b5471cc4c2604c4e0181989`.
- This checkpoint update is documentation-only and does not trigger Render deployment.

### Next actions

1. Verify the exact branch-head CI run and correct any failures before deployment.
2. If checks pass, request explicit owner approval before enabling the staging-only diagnostic flag and deploying the new code to the existing staging service.
3. After deployment and health verification, the signed-in owner can initiate one diagnostic email from `/admin/operations`. Confirm receipt in the actual mailbox; SMTP acceptance by the provider alone is not inbox-delivery proof.
4. Keep public registration disabled. Continue to design a separately guarded synthetic student invitation path only after the email diagnostic is verified.


## Password-reset feedback and staging deployment — 8 November 2026, 11:55 WAT

### Code and CI

The account page now provides explicit progress and result feedback for password-reset submission and password-reset completion, disables the submit control while a request is in flight, and restores it after completion/failure. An anonymous browser acceptance test covers the generic response for an unknown student email.

GitHub Actions run [42473078634](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42473078634), on commit `1768e43fb1e52cbd1673cf5a5f308d7cfa997cd7`, completed successfully:
- API unit/security tests: passed.
- Python, frontend/admin JavaScript and operations-script syntax: passed.
- Disposable PostgreSQL migration, schema, assessment/payment, registration-to-results, and local backup/restore rehearsals: passed.
- Anonymous and authenticated Playwright browser acceptance against disposable fixtures: passed.
- Non-publishing container build: passed.
- Staging health workflow job: passed (this workflow check ran before the deployment below).

### Render staging deployment

The existing Render service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) was manually deployed from its configured development branch `secondary-school-platform-foundation`.

- Deployment: `dep-dbo59ijl550s738opag0`
- Commit: `1768e43fb1e52cbd1673cf5a5f308d7cfa997cd7`
- Build: succeeded.
- Deployment: reached Render status `live` at 10:54:33Z; Render emitted `Your service is live`.
- Auto-deploy remains disabled.
- No production service, `main` branch, or PR merge was touched.

A fresh post-deploy HTTP `/health` response was not independently captured in this run. The CI staging-health job passed before this deployment; do not misrepresent it as post-deployment verification.

### SMTP and remaining release gates

The owner-only SMTP diagnostic code is included in this deployed commit, but `ADMIN_SMTP_DIAGNOSTIC_ENABLED` remains off by default and was not enabled in Render. No SMTP message was sent; Brevo delivery and password-reset email delivery remain unverified. No student account was created and public registration remains disabled.

R2 object-level acceptance, Paystack sandbox provider E2E, private audio storage/playback, managed recovery restoration, monitoring alert delivery, curriculum rights/teacher review, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, second administrator and independent security review remain outstanding. Do not activate exports, live payments, public onboarding or production release until the relevant evidence and approvals exist.


## Staging SMTP diagnostic enabled — 8 November 2026, 10:56 UTC

The owner explicitly requested enabling the protected SMTP diagnostic for a controlled delivery test. Render service `learnwise-staging-api` was updated with the non-secret feature flag:

- `ADMIN_SMTP_DIAGNOSTIC_ENABLED=true`

The existing SMTP credential values were not read, changed, or exposed. The change was applied only to the staging service. Render deployment `dep-dbo5aj95efls73ctfeeg` built successfully and reached status `live` at 10:56:50 UTC, using branch commit `30e02438ffaf55548c3b309d5483d704282b8258`. Render service auto-deploy remains disabled.

GitHub Actions checks for commit `30e02438ffaf55548c3b309d5483d704282b8258` completed successfully, including API tests, browser acceptance, container build, and staging-health job. The staging-health job preceded the environment-triggered deployment; it is not a post-deploy health result.

### SMTP diagnostic delivery — pending owner interaction

The diagnostic is available only to an authenticated owner administrator with the `settings.manage` permission, staging `APP_ENV`, CSRF protection and a separate one-attempt-per-hour rate limit. It sends a fixed token-free message to the signed-in administrator's own email address.

No diagnostic email has yet been sent, so Brevo delivery is **not verified**. To perform the authorised test, the owner must sign in at `https://learnwise-staging-api.onrender.com/admin/operations`, open the **Staging email delivery test** card, and press **Send test email to my admin address** once. Confirm receipt in the same mailbox and report whether it arrived (including spam/promotions folders if absent). Never paste SMTP credentials or verification/reset links into chat.

Account verification and password-reset email delivery remain unverified until an eligible controlled staging account exists and the full lifecycle is tested. Public student registration remains disabled.


## SMTP diagnostic attempt failed — 8 November 2026, 11:02 UTC

The owner initiated the staging-only SMTP diagnostic from the authenticated operations page. The endpoint returned `smtp_diagnostic_unavailable`; no delivery receipt was confirmed. Brevo delivery therefore remains **failed/unverified**.

Render application logs recorded three generic SMTP diagnostic failure warnings at 11:02:12, 11:02:17 and 11:02:26 UTC. The current implementation suppresses provider exception details, so these entries do not establish whether the cause was SMTP configuration/authentication, network/TLS, database rate-limit reservation, or audit persistence. The diagnostic rate-limit reservation occurs before SMTP submission; a failed initial attempt may therefore consume the one-per-hour allowance. Do not ask the owner to retry until the cause and retry window are understood.

GitHub Actions run [42473587753](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42473587753) subsequently completed all three jobs successfully:
- API/security tests, PostgreSQL migration/schema and disposable local restore rehearsals, and browser acceptance: passed.
- Post-deployment staging health check: passed.
- Non-publishing container build: passed.

A follow-up diagnostic observability change has now been committed on `secondary-school-platform-foundation`:
- The failure log and audit record will include only a bounded phase (`rate_limit_reservation`, `smtp_submission`, or `success_audit`) and exception class.
- Provider response text, credentials, addresses, hostnames and message content remain excluded.
- A regression test confirms sensitive exception text is not logged.
- Commit: `481442a4c2445dd66dae9d46a443bc8523e2bd1f`.
- CI for this follow-up commit has not yet been verified; it must pass before staging deployment.
- No SMTP credential values were read or changed. No additional email was sent.

The owner-only diagnostic remains enabled on staging. Public student registration remains disabled. No production deployment, PR merge, or change to `main` was made.


## Diagnostic observability deployed — 8 November 2026, 12:58 WAT

The diagnostic observability improvement was deployed to the existing staging service after its exact-commit workflow completed successfully.

- Code commit: `fa8d3377aac13068cc17801874c85a48c504a9e4`.
- Render deployment: `dep-dbo67aajnfac73e0kt2g`.
- Render result: `live`, completed at 11:58:08Z.
- GitHub Actions run: [42474098220](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42474098220), all three jobs completed successfully: API/security tests, post-deployment staging health, and non-publishing container build. Browser acceptance, PostgreSQL migrations/schema, assessment/payment tests, student journey, and disposable local backup/restore rehearsals passed within the API job.
- Render auto-deploy remains disabled. No production service, `main`, or PR merge was touched.

The improved diagnostic now records only the failure phase and exception class. It does not log provider response text or secrets. No second SMTP attempt was made; Brevo delivery remains failed/unverified until a controlled retry is authorised after the one-hour limit and the new logs are inspected.

## Work that can proceed without external credentials or appointments

- Draft release approval and sign-off templates are being consolidated in `RELEASE_GATE_REGISTER.md`. These are blank working templates, not approvals.
- Safe staging test-account design remains constrained by the need to distinguish synthetic QA records from real student records and never fabricate guardian consent. Public registration remains disabled.
- R2/audio live object tests still require provider credentials accessible to the staging runtime and safe test fixtures. Paystack provider E2E still requires sandbox credentials and an owner-controlled test.
- No managed recovery schedule, billable service, public onboarding, or live payment was enabled.
