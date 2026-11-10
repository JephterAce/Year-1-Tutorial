# Think Tank staging acceptance and operations checklist

This runbook creates a repeatable browser path for the existing staging service. It separates checks safe to run anonymously from checks requiring a designated test student or administrator. It does not deploy code, alter provider configuration, create accounts, send email, upload media, or execute migrations.

## 1. Browser acceptance path

A manual GitHub Actions workflow is available:

- Workflow: .github/workflows/think-tank-staging-browser.yml
- Test suite: browser-acceptance/staging.spec.js
- Default target: https://learnwise-staging-api.onrender.com
- Trigger: GitHub → Actions → Think Tank staging browser acceptance → Run workflow.
- The runner uses Chromium and uploads a Playwright report/trace artifact for 14 days.

The browser suite checks:

1. GET /health returns HTTP 200 and JSON status: ok.
2. Student home, account, assessment and lesson documents load in Chromium.
3. Registration, sign-in, password recovery and required consent controls render on the account page. It does not submit a real registration.
4. Anonymous student identity, profile, assessment-history, topic and attempt routes return 401.
5. Anonymous attempt creation, private audio authorization and private audio streaming return 401.
6. GET /api/v1/admin/auth/me returns 401 without an administrator session.
7. Anonymous visits to /admin, /admin/operations and /admin/reviews redirect to the dedicated /admin/login page; admin login and preview documents carry X-Robots-Tag: noindex.

### What the browser suite does not yet prove

- A successful student registration requires registration to be enabled, a real SMTP delivery path, a verified inbox and a disposable test identity. Registration must remain disabled until email delivery and the privacy/safeguarding release gates are cleared.
- Successful student login requires a designated staging-only test account. Do not use a real learner account.
- Full assessment completion requires an approved, published staging assessment and a designated test student.
- Lesson/audio playback requires a published approved lesson asset, a test entitlement and working private-storage credentials. The staging bucket was empty at the last audit.
- Admin page access and administrator API authentication are checked anonymously. A successful administrator sign-in and capability test still requires the owner bootstrap and an owner-approved staging administrator.
- The admin workspace remains a non-connected preview shell; protecting its route does not mean that CMS, finance or publishing operations are complete.

A successful workflow run is evidence only for the exact deployed staging target and commit tested. The app's existing Render deployment is behind the current development branch. Do not interpret a browser run against the old live SHA as validation of code that has not been deployed.

## 2. Render environment verification — private operator check

Target service:

- Workspace: Emmanuel's workspace
- Service: learnwise-staging-api
- ID: srv-dbkqcmt9fdbs73c2kdpg
- Dashboard: https://dashboard.render.com/web/srv-dbkqcmt9fdbs73c2kdpg

Render's service inspection does not reveal environment-variable values. An authorized operator must inspect them privately in the Render Dashboard. Never paste or screenshot secret values into chat, GitHub issues, source files or logs.

### Database target

Open the service's Environment page and privately confirm:

- DATABASE_URL host/endpoint corresponds to Neon branch ID br-still-cherry-baz7g5hk (branch name think-tank-staging).
- The database path/name is exactly learnwise.
- The URL uses the staging application role learnwise_app, not the migration owner role.
- The credential is valid and TLS is enabled.

Cross-check against Neon Console → project learnwise → branch think-tank-staging → connection details. Compare host and database name locally in the Dashboard; do not disclose username/password or full URI. Do not infer the branch from the database name alone.

### Private audio target

Privately confirm these non-secret values:

| Variable | Expected value |
|---|---|
| AUDIO_STORAGE_BACKEND | neon_s3 |
| AWS_ENDPOINT_URL_S3 | https://br-still-cherry-baz7g5hk.storage.c-8.eu-central-1.aws.neon.tech |
| AWS_REGION | eu-central-1 |
| AUDIO_STORAGE_BUCKET | learnwise-private-audio |

Also confirm the dedicated Cloudflare R2 audio credentials are present:
- AUDIO_STORAGE_ACCESS_KEY_ID
- AUDIO_STORAGE_SECRET_ACCESS_KEY

The expected dedicated audio settings are:
- AUDIO_STORAGE_ENDPOINT_URL_S3: https://<CLOUDFLARE_ACCOUNT_ID>.r2.cloudflarestorage.com
- AUDIO_STORAGE_REGION: auto
- AUDIO_STORAGE_BUCKET: learnwise-private-audio
- AUDIO_STORAGE_BACKEND: neon_s3 (the current application adapter name; it uses the configured S3-compatible endpoint)

The access key and secret must come from the separate R2 token scoped to the learnwise-private-audio bucket. Do not reuse the think-tank-private-exports token. The legacy AWS_* variables are fallback aliases only; do not overwrite them as part of this check.

Do not reveal or copy secret values. Do not use public-read access. Do not upload/delete/rename objects as part of this manual configuration check. The authenticated synthetic storage acceptance diagnostic performs its own temporary upload, retrieval, unsigned-access denial and deletion checks.

Record only a checklist outcome (match/mismatch/not checked), not values or secrets. If any item mismatches, stop and obtain owner approval before changing it. The Render environment-variable mutation tool is not a read-only inspection mechanism; do not use it to guess or overwrite unknown values. Any approved environment change must be coordinated with a reviewed deploy because environment updates may cause a restart/redeploy.

## 3. Owner administrator bootstrap

The staging database had zero administrator accounts at the last count-only audit. The one-time script is backend/bootstrap_admin.py; it has not been executed.

**Owner decision required:** select the exact email address that will own the first Think Tank administrator account. Do not use a shared mailbox unless the owner confirms it is controlled and secured.

After the owner chooses the address:

1. Confirm privately that the Render service's DATABASE_URL points to Neon branch br-still-cherry-baz7g5hk, database learnwise, and the least-privilege application role learnwise_app. Do not replace the service runtime role with an owner credential.
2. Confirm there is still no administrator account, using a count-only query.
3. Generate a unique password of at least 12 characters in a password manager. Do not send it through chat or commit it.
4. Run the script once from a trusted one-time operator environment using a separate staging-only bootstrap connection with the required INSERT privileges (the verified staging owner role learnwise_owner, or a narrowly scoped temporary bootstrap role). That connection must target branch br-still-cherry-baz7g5hk and database learnwise; do not change the Render service's DATABASE_URL. Set LEARNWISE_ADMIN_EMAIL, LEARNWISE_ADMIN_PASSWORD, and LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN only in that ephemeral environment.
5. Confirm exactly one administrator was created and that the audit event exists. Remove bootstrap variables immediately and discard the temporary connection environment.
6. Test administrator login, session expiry/logout, CSRF enforcement and role/capability checks in the browser suite or a controlled manual session.

The script is guarded by explicit confirmation, a transaction-scoped advisory lock and an any-existing-admin refusal. Never run it against production or an unverified database. Do not execute it until the owner email is selected and the target is verified.

## 4. Render health-check configuration

The Flask application implements GET /health. With DATABASE_URL configured it performs a database readiness check and returns 200 only when the database is ready; otherwise it returns 503. Render currently has no HTTP health-check path configured.

**Do not configure the Render health-check path yet.** First run the manual browser workflow against the deployed service and confirm the health test passes (HTTP 200, JSON status: ok) repeatedly. If it fails, investigate the deployment/database connection without changing the health-check setting. After a passing result, an authorized operator may set the Render service health-check path to /health in the Dashboard, save, and observe service events/deploy state. Verify that Render health checks remain green. Do not trigger a deploy merely to test a path.

Render considers an HTTP health check healthy when the endpoint returns a 2xx or 3xx response within five seconds. A 4xx/5xx response is unhealthy. The endpoint should test operation-critical readiness, not just process existence. See https://render.com/docs/health-checks.

## 5. Current blockers and release boundaries

- Registration and real SMTP verification remain blocked.
- No staging test student has been provisioned.
- No owner administrator has been selected or bootstrapped.
- No approved lesson/audio content or test entitlement exists.
- Render secret values remain privately unverified.
- Browser acceptance is now automatable, but the manual workflow has not yet been run against the live service.
- Render health-check path remains unset until the live /health test passes.
- No migrations, production deploys, live payments, public audio changes, legacy Telegram bot changes or resource deletions are authorized by this runbook.
