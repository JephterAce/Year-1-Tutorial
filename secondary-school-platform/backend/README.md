# Learnwise backend

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
2. Apply migrations `001_platform_hardening.sql` through `012_assessment_issue_reporting.sql` in numeric order.
3. Rehearse on a disposable database, inspect constraints/indexes, and verify rollback/restore before any production migration.
4. Run the application with a least-privilege database role.

No migration has been applied to a live database.

## Student identity

Registration requires explicit Terms and Privacy acceptance. The API supports email verification, login/logout, session revocation, CSRF validation and password reset. The account page assumes a same-origin API or reviewed same-origin reverse proxy. Production requires HTTPS, reviewed origin/CSRF policy, proxy-aware rate limiting, email resend/abuse controls, transactional email outbox and a real PostgreSQL/SMTP end-to-end test.

## Assessment execution

The attempt service creates a briefing-state attempt, checks class eligibility/attempt limits/allowed question counts, and starts only after affirmative agreement to the current briefing policy version. Start populates immutable per-attempt question and answer-key snapshots. Student projections omit answer keys. Server UTC deadlines enforce the 36-seconds-per-question rule, with the 10-question/7-minute exception. Answers are ownership-checked and saved server-side. Submission/expiry grades supported objective types and persists results. Focus/visibility/fullscreen incidents are debounced; the first two warn and the third terminates with an integrity-review flag, not a finding of misconduct.

The browser countdown is display-only. A production client must autosave answers, send integrity events, keep the server deadline visible, and submit persisted answers on expiry. This increment has unit/contract coverage but has not been exercised against PostgreSQL. It does not yet provide an appeal workflow, fault-reporting workflow, robust recovery for concurrent/retried requests, result notifications, admin assessment authoring, or end-to-end browser tests. No essays, handwriting, proofs, webcam or microphone surveillance are supported.

## Payment and owner email

The callback validates the raw Paystack HMAC signature, looks up a server-created pending order, verifies the transaction directly with Paystack, and atomically records payment/entitlement/outbox state. The outbox worker supports leased claims and retries but is not scheduled or monitored. A server-priced checkout initialisation route now creates a pending order from the published topic price and verified student account, then initialises Paystack using the server secret. It returns only a validated HTTPS Paystack checkout URL. Payment reconciliation/refunds, a scheduled outbox worker, production monitoring, end-to-end database/provider tests and operational controls remain. Real payments must remain disabled until reviewed and explicitly approved. SMTP notification recipient defaults to `emmanuelbjephter@gmail.com`; configure SMTP and Paystack credentials only in the host's secret manager, never in source control or chat. No live email or payment has been tested.

## Release gates

- Dedicated PostgreSQL provisioned; migrations 001–012 rehearsed and applied only after approval.
- SMTP and HTTPS public app URL configured privately; email delivery/resend and operational monitoring tested.
- Payment order creation, reconciliation/refunds, outbox scheduling and alerting implemented before live checkout.
- Revised NERDC curriculum versioning, source capture, cohort applicability and teacher-review workflow implemented; authorised source documents and term schemes still required. No invented topic/term mapping.
- Nigerian privacy, data-protection, minor-consent, accessibility and safeguarding review completed.
- Security review, production monitoring, backup/restore and incident response tested.

Keep PR #1 draft and unmerged. Do not deploy, apply production migrations, activate live payments, change production secrets/config, spend money, or modify the legacy bot without explicit approval.


## Revised NERDC curriculum workflow

Learnwise targets the revised 2025 NERDC Senior Secondary Education Curriculum across SS1–SS3 for the six selected subjects. Migrations 009–010 add curriculum-version records, cohort applicability records, source rights/provenance metadata, optional term assignment and a database trigger that rejects unsupported topic publication. Cohort applicability remains pending until official evidence confirms it.

Use `../CURRICULUM_WORKFLOW.md` and `../CURRICULUM_IMPORT_TEMPLATE.csv` to capture source-grounded curriculum metadata. `curriculum_import.py` parses the CSV template, supports a dry-run validation report and blocks publication unless the source, exact source section, teacher approval and rights status are present. The published catalogue now requires the target curriculum version, an approved source record and an explicitly published curriculum review state. Topics with unknown term placement must not be presented as term-specific lessons.

Migrations 009–012 are authored only; no database has been migrated. The validator has unit tests, but CI and a disposable PostgreSQL migration rehearsal are still required. NERDC portal access must not be bypassed, and public metadata does not grant permission to reproduce full curriculum documents.


Migration 011 makes source records immutable once referenced by a published topic and prevents material changes to a curriculum version while published topics use it. Corrections must use a replacement source/version and pass review; migration execution and PostgreSQL trigger behaviour still require disposable-database rehearsal.


## Assessment issue reporting

Migration 012 adds student-owned reports for integrity appeals, question errors and technical problems. Authenticated students can submit reports against their own attempts and retrieve only their own report status. Question-error reports must reference a valid UUID for a question in that attempt; integrity appeals are accepted only for integrity-terminated attempts. Details are length-limited and each attempt is capped at five reports. Submission locks the owning attempt row while checking/inserting the report, serialising concurrent submissions so parallel requests cannot bypass the per-attempt cap. This is a student submission path only: a privileged admin review queue and staff response workflow are still required before launch.


## Student-data export serialization

`export_serialization.py` provides allowlist-only JSON/CSV serialization, normalises dates/UUIDs/decimals, rejects unsupported values, and neutralises spreadsheet formula injection in text cells while preserving numeric values. It is deliberately not an export endpoint: authentication, role authorisation, consent/legal basis, audit logging, bounded database queries, private storage, expiring downloads and deletion/retention workflows must exist before any student data is exported. Unit tests cover field exclusion and CSV/JSON safety.


## Administrative capability policy

`admin_policy.py` defines a default-deny capability matrix for owner, editor, reviewer, support and analyst roles. Inactive or unknown principals and unknown capabilities are denied. It is a policy primitive only: admin login/session authentication, server-side principal loading, endpoint decorators, audit events and role assignment controls must be implemented and tested before exposing admin APIs.


## Admin security foundation (migration 013)

Migration `013_admin_sessions_and_audit_guard.sql` adds a separate server-side admin session table with hashed session and CSRF tokens, expiry/revocation fields and active-session indexes. It also makes audit events append-only and adds case/space-insensitive admin email lookup. The migration does not enable admin login or grant access by itself. A dedicated admin authentication service, secure cookie/CSRF routes, capability enforcement, audit-writing wrappers and controlled owner provisioning are still required. Rehearse this migration on disposable PostgreSQL before any deployment.
