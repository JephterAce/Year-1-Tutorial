# Think Tank staging environment — 2026-11-03

## Confirmed Render resource

| Field | Verified value |
|---|---|
| Service | `learnwise-staging-api` |
| Service ID | `srv-dbkqcmt9fdbs73c2kdpg` |
| Workspace | Emmanuel's workspace |
| URL | https://learnwise-staging-api.onrender.com |
| Branch configured in Render | `secondary-school-platform-foundation` |
| Region / plan | Frankfurt / Free |
| Runtime | Docker; context `secondary-school-platform`; Dockerfile `secondary-school-platform/backend/Dockerfile` |
| Auto deploy | Disabled |
| Render health-check path | Not configured |
| Current live deployment | `fe9ff76f7b3b53331bfd4179062d7d38ac273d23` |
| Current GitHub branch head at audit | `96a4afa508f03e94197326407af6121bacc5ad44` |

At the initial comparison, the branch head was nine commits ahead of the live deployment; subsequent audit commits added owner-bootstrap hardening, tests and runbook corrections. The original nine-commit comparison contained documentation and student/admin HTML/CSS changes; no backend, migration or storage-adapter files were in that comparison. The later bootstrap changes are not deployed. Do not assume browser acceptance has passed: live HTTP/browser checks remain outstanding. The Flask application exposes `/health`; Render's service-level health-check path is currently blank.

## Application URLs

- Student home: https://learnwise-staging-api.onrender.com/
- Account: https://learnwise-staging-api.onrender.com/account
- Assessment: https://learnwise-staging-api.onrender.com/assessment
- Lesson: https://learnwise-staging-api.onrender.com/lesson
- Admin workspace: https://learnwise-staging-api.onrender.com/admin
- Admin operations: https://learnwise-staging-api.onrender.com/admin/operations
- Assessment reviews: https://learnwise-staging-api.onrender.com/admin/reviews
- Health: https://learnwise-staging-api.onrender.com/health

Admin pages carry a noindex header. Their API data routes require an authenticated admin session and capability checks.

## Neon database — awaiting live verification

The prior staging handover records the following Neon resources, but they have not yet been independently queried in this audit:

- Project: `think_tank`, project ID `spring-cloud-84267029`
- Staging branch: `think_tank-staging-rehearsal`, branch ID `br-still-cherry-baz7g5hk`
- Database: `think_tank`, PostgreSQL 16
- Expected baseline: `DATABASE_SCHEMA.sql` followed by `backend/migrations/001`–`013`
- Expected migration ledger: `think_tank_migration_history`
- Expected application role: `think_tank_app`, distinct from the owner role

Do not treat the migration ledger, database connectivity, role grants or current branch selection as verified until the Neon connector can query this exact project and branch. Do not apply or replay migrations during reconciliation. Never paste database connection strings or credentials into Git, tickets or chat.

## Private audio — bucket identity requires reconciliation

The current backend S3 adapter reads these environment variable names:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ENDPOINT_URL_S3`
- `AWS_REGION`
- `AUDIO_STORAGE_BUCKET`

The checked-in audio storage tests use `learnwise-private-audio`. An earlier staging note records `think_tank-private-audio`. Neither the live Render environment values nor the bucket's actual Neon branch scope/policy have been read in this audit. Therefore the live bucket name, private policy, endpoint, credential validity and object inventory remain **unverified**. Do not upload, delete, rename or expose objects until the exact bucket is confirmed read-only through Neon.

The code supports private upload to pending review, separate reviewer approval, authenticated entitlement-checked streaming and byte-range forwarding. The current adapter validates object keys and file size/type/signatures at the upload route. Malware scanning and approved audio assets remain release requirements.

## Email and payments

- Brevo transactional email has been selected, but sender identity and SMTP credentials/delivery are not verified.
- Student registration remains disabled pending email and safeguarding gates.
- Paystack checkout remains disabled pending real sandbox credentials and end-to-end sandbox acceptance.
- No live payment should be attempted.

## First owner administrator

There is no public administrator sign-up. The one-time script is `backend/bootstrap_admin.py`. From a trusted environment, after confirming the staging database target and selecting the owner's intended email, set:

- `DATABASE_URL` — staging database only; never paste it into chat.
- `LEARNWISE_ADMIN_EMAIL`
- `LEARNWISE_ADMIN_PASSWORD` — unique, strong password of at least 12 characters.
- `LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN`

The script hashes the password using scrypt, requires explicit confirmation, acquires a transaction-scoped advisory lock and refuses to run if **any** admin account already exists. It records an audit event. Remove bootstrap variables from the environment immediately after success. Do not run it until the Neon staging branch and database role are independently verified. Never send the password through chat or commit it to Git.

## Safety and release decision

This is staging only. No production deployment, real student data, public registration, public audio or live payment is approved. Keep PR #1 draft and unmerged, keep `main` untouched, and do not enable auto deploy. Close the external release gates in `RELEASE_GATE_REGISTER.md` before onboarding learners.
