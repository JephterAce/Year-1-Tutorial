# Think Tank backend

Isolated Flask/PostgreSQL API for the SS1–SS3 learning platform. The existing Year 1 Telegram bot is outside this application.

## Local development

```bash
cd secondary-school-platform/backend
python -m venv .venv
# Activate the virtual environment
pip install -r requirements.txt
python -m unittest -v
python app.py
```

- Health: `GET /health`
- Catalogue: `GET /api/v1/catalogue`
- Student account: `/api/v1/auth/*`
- Private student profile: `GET/PATCH /api/v1/student/profile`
- Assessment execution: `/api/v1/assessments/{assessment_id}/attempts` and `/api/v1/assessment-attempts/{attempt_id}/*`
- Lesson checkout: `POST /api/v1/topics/{topic_id}/checkout` (server-priced; provider credentials required)
- Paystack callback: `POST /api/v1/webhooks/paystack` (development foundation only)

Without `DATABASE_URL`, only the clearly labelled demo catalogue is available. Identity, assessment and payment operations require PostgreSQL and fail closed without it. Use a dedicated TLS PostgreSQL database and never commit real environment files or credentials.

## Ordered database setup

1. Apply `../DATABASE_SCHEMA.sql` using a migration-owner role.
2. Apply migrations `001_platform_hardening.sql` through `013_admin_sessions_and_audit_guard.sql` in numeric order. The dedicated Neon staging branch has already had the baseline schema and migrations 001–013 applied and recorded; do not replay them manually against that branch. Use a disposable database for repeatable rehearsals.
3. Rehearse on a disposable database, inspect constraints/indexes, and verify rollback/restore before any production migration.
4. Run the application with a least-privilege database role.

The isolated Neon staging branch is migrated. No production database has been provisioned or migrated.

## Student identity

Registration requires explicit Terms and Privacy acceptance. The API supports email verification, login/logout, session revocation, CSRF validation and password reset. The account page assumes a same-origin API or reviewed same-origin reverse proxy. Production requires HTTPS, reviewed origin/CSRF policy, proxy-aware rate limiting, email resend/abuse controls, transactional email outbox and a real PostgreSQL/SMTP end-to-end test.

## Assessment execution

The attempt service creates a briefing-state attempt, checks class eligibility/attempt limits/allowed question counts, and starts only after affirmative agreement to the current briefing policy version. Start populates immutable per-attempt question and answer-key snapshots. Student projections omit answer keys. Server UTC deadlines enforce the 36-seconds-per-question rule, with the 10-question/7-minute exception. Answers are ownership-checked and saved server-side. Submission/expiry grades supported objective types and persists results. Focus/visibility/fullscreen incidents are debounced; the first two warn and the third terminates with an integrity-review flag, not a finding of misconduct.

The browser countdown is display-only. A production client must autosave answers, send integrity events, keep the server deadline visible, and submit persisted answers on expiry. This increment has unit/contract coverage but has not been exercised against PostgreSQL. It does not yet provide an appeal workflow, fault-reporting workflow, robust recovery for concurrent/retried requests, result notifications, admin assessment authoring, or end-to-end browser tests. No essays, handwriting, proofs, webcam or microphone surveillance are supported.

## Payment and owner email

The callback validates the raw Paystack HMAC signature, looks up a server-created pending order, verifies the transaction directly with Paystack, and atomically records payment/entitlement/outbox state. The outbox worker supports leased claims and retries but is not scheduled or monitored. A server-priced checkout initialisation route now creates a pending order from the published topic price and verified student account, then initialises Paystack using the server secret. It returns only a validated HTTPS Paystack checkout URL. Payment reconciliation/refunds, a scheduled outbox worker, production monitoring, end-to-end database/provider tests and operational controls remain. Real payments must remain disabled until reviewed and explicitly approved. SMTP notification recipient defaults to `emmanuelbjephter@gmail.com`; configure SMTP and Paystack credentials only in the host's secret manager, never in source control or chat. No live email or payment has been tested.

## Release gates

- Dedicated production PostgreSQL provisioned; staging Neon branch already has baseline schema and migrations 001–013 applied. Production migration plan, backup and restore rehearsal still required.
- SMTP and HTTPS public app URL configured privately; email delivery/resend and operational monitoring tested.
- Payment order creation, reconciliation/refunds, outbox scheduling and alerting implemented before live checkout.
- Revised NERDC curriculum versioning, source capture, cohort applicability and teacher-review workflow implemented; authorised source documents and term schemes still required. No invented topic/term mapping.
- Nigerian privacy, data-protection, minor-consent, accessibility and safeguarding review completed.
- Security review, production monitoring, backup/restore and incident response tested.

Keep PR #1 draft and unmerged. Do not deploy, apply production migrations, activate live payments, change production secrets/config, spend money, or modify the legacy bot without explicit approval.


## Revised NERDC curriculum workflow

Think Tank targets the revised 2025 NERDC Senior Secondary Education Curriculum across SS1–SS3 for the six selected subjects. Migrations 009–010 add curriculum-version records, cohort applicability records, source rights/provenance metadata, optional term assignment and a database trigger that rejects unsupported topic publication. Cohort applicability remains pending until official evidence confirms it.

Use `../CURRICULUM_WORKFLOW.md` and `../CURRICULUM_IMPORT_TEMPLATE.csv` to capture source-grounded curriculum metadata. `curriculum_import.py` parses the CSV template, supports a dry-run validation report and blocks publication unless the source, exact source section, teacher approval and rights status are present. The published catalogue now requires the target curriculum version, an approved source record and an explicitly published curriculum review state. Topics with unknown term placement must not be presented as term-specific lessons.

Migrations 009–013 are applied on the isolated Neon staging branch and rehearsed in disposable PostgreSQL CI. No production database has been migrated. The validator has unit tests, and CI rehearses all migrations on disposable PostgreSQL. The dedicated Neon staging branch also has migrations 001–013 recorded. Authorised source acquisition and teacher review remain required. NERDC portal access must not be bypassed, and public metadata does not grant permission to reproduce full curriculum documents.


Migration 011 makes source records immutable once referenced by a published topic and prevents material changes to a curriculum version while published topics use it. Corrections must use a replacement source/version and pass review; migration execution and PostgreSQL trigger behaviour still require disposable-database rehearsal.


## Assessment issue reporting

Migration 012 adds student-owned reports for integrity appeals, question errors and technical problems. Authenticated students can submit reports against their own attempts and retrieve only their own report status. Question-error reports must reference a valid UUID for a question in that attempt; integrity appeals are accepted only for integrity-terminated attempts. Details are length-limited and each attempt is capped at five reports. Submission locks the owning attempt row while checking/inserting the report, serialising concurrent submissions so parallel requests cannot bypass the per-attempt cap. This is a student submission path only: a privileged admin review queue and staff response workflow are still required before launch.


## Student-data export serialization

`export_serialization.py` provides allowlist-only JSON/CSV serialization, normalises dates/UUIDs/decimals, rejects unsupported values, and neutralises spreadsheet formula injection in text cells while preserving numeric values. It is deliberately not an export endpoint: authentication, role authorisation, consent/legal basis, audit logging, bounded database queries, private storage, expiring downloads and deletion/retention workflows must exist before any student data is exported. Unit tests cover field exclusion and CSV/JSON safety.


## Administrative capability policy

`admin_policy.py` defines a default-deny capability matrix for owner, editor, reviewer, support and analyst roles. Inactive or unknown principals and unknown capabilities are denied. It is a policy primitive only: admin login/session authentication, server-side principal loading, endpoint decorators, audit events and role assignment controls must be implemented and tested before exposing admin APIs.


## Admin security foundation (migration 013)

Migration `013_admin_sessions_and_audit_guard.sql` adds a separate server-side admin session table with hashed session and CSRF tokens, expiry/revocation fields and active-session indexes. It also makes audit events append-only and adds case/space-insensitive admin email lookup. The migration does not enable admin login or grant access by itself. The staging database has the migration applied; no owner account has been bootstrapped yet. A dedicated admin authentication service, secure cookie/CSRF routes, capability enforcement, audit-writing wrappers and controlled owner provisioning are still required. Rehearse this migration on disposable PostgreSQL before any deployment.


## Admin authentication service

admin_auth.py authenticates pre-provisioned admin accounts against the dedicated admin table, applies an HMAC-keyed login rate limit, issues random server-side sessions with only token hashes stored, revokes prior sessions on login, checks active status on every session lookup, validates CSRF tokens, and supports revocation on logout. Flask routes expose admin login, current-session inspection and logout only. There is deliberately no public admin signup or role-change endpoint. Privileged admin business operations must still be wrapped in capability checks and append-only audit events before they are exposed.


## Private audio storage adapter

The API supports the local private filesystem for development and Neon branch-scoped S3-compatible storage for staging. Set `AUDIO_STORAGE_BACKEND=neon_s3`, `AUDIO_STORAGE_BUCKET`, and the branch-scoped `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, and `AWS_REGION` values in the host secret manager. The S3 bucket must remain private. Audio requests still require a student session, published topic, approved asset, active entitlement and short-lived Think Tank token; the API streams objects through the same-origin endpoint and forwards byte-range requests. Never expose S3 credentials or object-store URLs to the browser.


## One-time owner administrator bootstrap

There is deliberately no public administrator registration. To create the first owner, run `python bootstrap_admin.py` from a trusted environment with the staging `DATABASE_URL`, `LEARNWISE_ADMIN_EMAIL`, and a strong `LEARNWISE_ADMIN_PASSWORD` set in that environment, plus `LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN`. The script refuses to overwrite an existing account, hashes the password with scrypt, and records an audit event. Do not put the database URL or password in source control, browser code, or chat. Remove the bootstrap environment variables immediately after successful execution.


## AI tutor foundation (not enabled for learners)

- `POST /api/v1/tutor/answer` is a student-session and CSRF-protected endpoint. It takes a bounded question and optional lesson context; class level is read from the authenticated student session, not trusted from the browser.
- `ai_tutor.py` provides an OpenAI-compatible chat-completions adapter with HTTPS endpoint validation, exact hostname allow-listing, redirect blocking, request/response size bounds, timeout and a short output-token cap. Provider credentials are read only from environment variables.
- Configure `AI_API_URL`, `AI_API_ALLOWED_HOSTS`, `AI_API_KEY` and `AI_MODEL` privately in the host. Never commit or paste the key into chat.
- `AI_TUTOR_ENABLED` is a strict opt-in and defaults to disabled. **Do not enable it for staging learners or production yet:** durable per-student request quotas, spend limits/budget alerts, retention controls and the complete learner UI have not been implemented or reviewed. The provider adapter and protected API route are an initial foundation, not a launch-ready AI tutor.
- AI answers are educational assistance only. They do not grade assessments, grant paid access, publish curriculum or replace qualified teacher review. Provider responses must be evaluated for factual accuracy, age suitability, bias and curriculum alignment before wider use.


### AI tutor usage limits and cost reservations

- Migration `014_ai_tutor_usage_limits.sql` adds per-student UTC daily usage accounting; migration `017_ai_tutor_platform_budget.sql` adds platform-wide daily usage accounting. The service serializes reservations with PostgreSQL advisory transaction locks and checks per-student daily/monthly request limits, per-student spend caps, and global platform daily/monthly spend caps before a provider request.
- The reservation is conservative: it estimates input tokens from the bounded prompt and reserves the full configured output-token ceiling. Failed provider attempts remain counted, preventing retry loops from bypassing quotas. This is an upper-bound reservation, not a provider invoice reconciliation.
- Configure the request/budget caps and exact selected-model input/output price rates privately. Price values are integer micro-USD per one million tokens. Missing/invalid pricing fails closed. Revisit price rates whenever the model/provider tariff changes.
- The database migration has been added to the development branch but has **not** been applied to managed staging. The feature flag remains disabled. Do not enable learner access until migration rehearsal, rate/pricing configuration, privacy review, concurrency tests and monitoring are complete.


### Reviewed lesson content and podcast production

- Migration `015_reviewed_lesson_content_and_progress.sql` adds versioned lesson-content JSON, separate practice-question records, and student topic completion records.
- Authenticated students with an active topic entitlement can read only published topic content that has an approved lesson-content version. Student projections omit answer keys. Practice submissions are checked server-side; completion writes are CSRF-protected.
- Admin authors with `curriculum.edit` can submit lesson content and practice questions as drafts. Admins with `curriculum.publish` can approve or reject a draft and must provide the teacher-reviewer's name. Approval promotes its practice questions at the same time. The lesson content itself does not publish the curriculum topic; the topic must separately pass source, cohort, term and publication guards.
- Migration `016_podcast_script_workflow.sql` adds a versioned script register. Admins with `audio.upload` can generate an original two-presenter script draft from approved lesson content. They can upload a recorded or externally generated TTS file through the existing private audio upload route, attach the pending podcast asset to the script, and send the script/audio through separate review. A podcast script can be approved only when its attached private podcast audio is approved.
- This is a controlled production pipeline, not yet an automatic TTS service. No voice-provider credentials are configured and no audio was generated or uploaded in this implementation. The private streaming/entitlement route remains the delivery path after topic publication and asset approval.
- The first Biology SS1 curriculum source was captured as an official October 2025 NERDC PDF; a topic map and one original draft lesson are in `content/curriculum-drafts/biology/`. They remain drafts and are not in the student catalogue.
