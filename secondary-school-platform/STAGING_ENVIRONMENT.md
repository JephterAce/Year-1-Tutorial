# Think Tank staging environment — verified 2026-11-03

This document distinguishes verified provider state from configuration that is not readable through the available provider interfaces. No migrations were replayed, no secrets were read or changed, and no deployment was triggered during this audit.

## Render service

| Field | Verified value |
|---|---|
| Workspace | Emmanuel's workspace |
| Service | `learnwise-staging-api` |
| Service ID | `srv-dbkqcmt9fdbs73c2kdpg` |
| URL | https://learnwise-staging-api.onrender.com |
| Repository | `JephterAce/Year-1-Tutorial` |
| Configured branch | `secondary-school-platform-foundation` |
| Runtime | Docker |
| Docker context | `secondary-school-platform` |
| Dockerfile | `secondary-school-platform/backend/Dockerfile` |
| Region / plan | Frankfurt / Free |
| Auto deploy | Disabled |
| Health-check path | Not configured |
| Current live deployment | `fe9ff76f7b3b53331bfd4179062d7d38ac273d23` |
| Current development branch head | `30f9f41500e2c0c504f2007bcc618609855cbc28` |
| Branch commits ahead of live deployment | 30 |

The live deployment is running, but it is 30 commits behind the current development branch. The later commits include student/admin presentation updates, runbook corrections and owner-bootstrap hardening/tests. Do not assume these changes are present in the live service. Auto deploy is disabled and no deployment was triggered.

The Flask app exposes `/health`, but the Render health-check path is blank. Direct requests to the health, student, assessment, lesson and admin URLs could not be completed from the available external browser/network environment. Render request-log query returned no request entries for the queried range. Therefore HTTP/browser acceptance remains **not verified**; this is not evidence that the service is down.

## Application URLs

- Student home: https://learnwise-staging-api.onrender.com/
- Account: https://learnwise-staging-api.onrender.com/account
- Assessment: https://learnwise-staging-api.onrender.com/assessment
- Lesson: https://learnwise-staging-api.onrender.com/lesson
- Admin workspace: https://learnwise-staging-api.onrender.com/admin
- Admin operations: https://learnwise-staging-api.onrender.com/admin/operations
- Admin sign-in: https://learnwise-staging-api.onrender.com/admin/login
- Assessment reviews: https://learnwise-staging-api.onrender.com/admin/reviews
- Health: https://learnwise-staging-api.onrender.com/health

Student-facing page routes are served normally. Administrator workspace, operations and review pages now redirect anonymous visitors to /admin/login; the administrator identity and data APIs remain session-authenticated and capability-checked. The dedicated browser acceptance workflow checks these boundaries against the live service.

## Neon PostgreSQL — live state verified read-only

| Field | Verified value |
|---|---|
| Project name / ID | `learnwise` / `spring-cloud-84267029` |
| Region | AWS Frankfurt (`eu-central-1`) |
| PostgreSQL | 16.15 |
| Staging branch / ID | `think-tank-staging` / `br-still-cherry-baz7g5hk` |
| Branch state | Ready |
| Default branch | `main` (`br-calm-wave-baaw8vpu`) — not used for staging audit |
| Database | `learnwise` |
| Owner role | `learnwise_owner` |
| Application role | `learnwise_app` |

The previous documentation incorrectly called the project/database `think_tank`, the staging branch `think_tank-staging-rehearsal`, and the migration ledger `think_tank_migration_history`. The live values above supersede those names.

### Migration ledger

The ledger is `public.learnwise_migration_history`, with columns `version`, `source_blob_sha` and `applied_at`. It contains migrations `001_platform_hardening` through `013_admin_sessions_and_audit_guard`. **All 13 recorded source blob hashes match the corresponding migration file blob hashes on the current GitHub development branch.** Migration 013's hash is `548e463479b322b4197e8a605f63d03b6993fdf8`.

This was a read-only verification. No migration was applied, altered, or replayed.

### Application-role permission check

A read-only query using `learnwise_app` successfully connected to database `learnwise`. The role can read the student table and migration ledger, but cannot update `admin_users` or `audit_events`. The owner role was used only for read-only Neon inspection; no account or permission changes were made.

At audit time, the staging database contained zero administrator accounts, zero student accounts and zero audit events. This is a count-only check; no student or administrator personal records were retrieved. The zero-admin state means the one-time owner bootstrap is still pending, not that it should be run automatically.

**Important unresolved connection check:** Render does not expose the value of its secret `DATABASE_URL` through the service inspection used here. The Neon staging branch/database are verified, but it is not yet proven that the running Render service's `DATABASE_URL` points to this exact branch and database. Verify privately in Render before running the bootstrap.

## Neon private audio storage — live state verified read-only

| Field | Verified value |
|---|---|
| Storage | Enabled on `think-tank-staging` |
| S3 endpoint | `https://br-still-cherry-baz7g5hk.storage.c-8.eu-central-1.aws.neon.tech` |
| Region | `eu-central-1` |
| Addressing | Path-style |
| Bucket | `learnwise-private-audio` |
| Access level | `private` |
| Object inventory | Empty at audit time |

The previous documentation's `think_tank-private-audio` name was incorrect for this staging branch. The current backend adapter reads these variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ENDPOINT_URL_S3`
- `AWS_REGION`
- `AUDIO_STORAGE_BUCKET`

Expected non-secret Render values for this Neon staging branch are:

- `AWS_ENDPOINT_URL_S3=https://br-still-cherry-baz7g5hk.storage.c-8.eu-central-1.aws.neon.tech`
- `AWS_REGION=eu-central-1`
- `AUDIO_STORAGE_BUCKET=learnwise-private-audio`

The adapter configures S3 path-style addressing. Render's secret values are not readable in the service inspection used for this audit, so it is **not verified** that the live Render environment matches these expected values or that its credentials authenticate successfully. Do not print or paste credentials. Do not upload, delete, rename or make any audio public as part of verification.

The code supports private upload to pending review, separate reviewer approval, authenticated entitlement-checked streaming and byte-range forwarding. Malware scanning and approved audio assets remain release requirements.

## CI status

The latest workflow run at the time of this update is [run 41644750663](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/41644750663). Both `api-tests` and `container-build` passed. The API test job includes unit/security tests, JavaScript syntax checks, disposable PostgreSQL migration rehearsal, schema integration and assessment/payment integration tests. These are CI tests against disposable PostgreSQL and stubbed payment-provider responses, not live Neon migration replay or Paystack sandbox checkout.

The initial bootstrap-test mock failure was corrected in `test_bootstrap_admin.py`; subsequent runs passed.


## Email and payments

- Brevo transactional email has been selected, but sender identity, SMTP credentials and real delivery remain unverified.
- Student registration must remain disabled pending email and safeguarding/privacy release gates.
- Paystack checkout must remain disabled pending provider sandbox credentials and full sandbox acceptance.
- No live payment should be attempted.

## First owner administrator

There is no public administrator sign-up. The hardened one-time script is `backend/bootstrap_admin.py`. Do not run it until the owner selects the intended email and the operator privately verifies that `DATABASE_URL` targets the Neon staging branch/database above.

Set these variables only in a trusted, ephemeral operator environment. Use the verified staging owner role or a narrowly scoped bootstrap role for the one-time insert; do not change the Render service's least-privilege `DATABASE_URL`:

- `DATABASE_URL` — one-time staging bootstrap connection only; never paste it into chat.
- `LEARNWISE_ADMIN_EMAIL`
- `LEARNWISE_ADMIN_PASSWORD` — unique password, at least 12 characters.
- `LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN`

The script hashes the password using scrypt, requires explicit confirmation, acquires a transaction-scoped advisory lock, refuses to run if **any** administrator already exists, and writes an audit event. The script has not been run. Remove bootstrap variables immediately after a successful run. Never send the password through chat or commit it to Git.

## Safety and release decision

This is staging only. No production deployment, real student data, public registration, public audio or live payment is approved. Keep PR #1 draft and unmerged, keep `main` untouched, keep Render auto deploy disabled, and do not run migrations as part of reconciliation. Close the external release gates in `RELEASE_GATE_REGISTER.md` before onboarding learners.


## Browser acceptance and operational follow-through

A manual Playwright workflow has been added at `.github/workflows/think-tank-staging-browser.yml`, with its test suite under `browser-acceptance/`. It runs Chromium against the existing staging URL and checks the health endpoint, student-facing page rendering, account form controls, anonymous student/assessment/private-audio API rejection, administrator identity rejection and noindex headers on admin preview pages. The workflow has not yet been manually dispatched against the live service.

The test suite intentionally does not submit a real registration or create student/admin accounts. Successful registration requires SMTP and a disposable test identity; successful login and assessment completion require owner-approved staging test accounts and published test content. See `STAGING_ACCEPTANCE_AND_OPERATIONS.md` for the complete workflow, environment verification checklist, bootstrap procedure and health-check gate.

Render's service configuration was rechecked on 2026-11-03: the HTTP health-check path remains blank. The deployed service SHA remains the historic live deployment recorded above unless separately verified; the new browser workflow does not deploy code. Do not set Render's health-check path to `/health` until the manual browser workflow confirms HTTP 200 with JSON status `ok`.

Render's secret environment values remain inaccessible through the available service inspection. An authorized operator must privately compare DATABASE_URL with Neon branch `br-still-cherry-baz7g5hk` and database `learnwise`, and verify the private audio settings documented in `STAGING_ACCEPTANCE_AND_OPERATIONS.md`. No environment variables were changed.

The first owner admin remains uncreated. The owner must select the exact administrator email before the guarded bootstrap script is run.


## Administrator page access hardening

The current development branch now includes a dedicated administrator sign-in page at `/admin/login`. The `/admin`, `/admin/operations` and `/admin/reviews` pages require a valid administrator session and redirect anonymous visitors to the login page. The login form uses the separate administrator login API; student credentials are not accepted as administrator credentials. Protected pages set no-store and noindex headers.

This change is committed on the development branch and is not present in the existing Render deployment until a separately approved staging deploy. The manual browser acceptance workflow includes assertions for these redirects and the admin login form.
