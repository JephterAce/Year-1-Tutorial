# Implementation status

Last updated: 2026-11-01

## Verified project state
- Work is isolated in `secondary-school-platform/` on `secondary-school-platform-foundation`.
- Draft pull request #1 remains open and unmerged: https://github.com/JephterAce/Year-1-Tutorial/pull/1
- Product scope: SS1–SS3 and six subjects — English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics.
- Student portal prototype at `frontend/index.html`; dashboard now displays six subjects. Sample topics are illustrative only and are not assigned to verified class-specific sequences or terms.
- Catalogue term filter now reflects the actual data state: term allocation pending verification. It does not imply verified First/Second/Third Term placement.
- Admin workspace at `admin/index.html` is now an interactive local prototype with working section navigation, curriculum coverage view, lesson brief preview, audio-library state, Channel announcement composer/copy workflow, and locked student/payment operations. It is still not connected to authentication or a database.
- Flask API, PostgreSQL repository, schema and three authored migrations are present. Migrations have NOT been applied to a live database.
- API demo mode is used without a dedicated `DATABASE_URL`; no production database or real student records are connected.
- Curriculum source register records official NERDC links and validation rules. Full topic-by-topic mapping for all 18 class-subject combinations remains outstanding.
- Telegram scope is a broadcast-only Channel for announcements and lesson updates. No student bot, group, private bot delivery or account-linking feature is in scope. The separate university bot `@Ustpaymentbot` remains untouched.
- No production deployment, domain, payment integration, secure audio delivery or AI narration workflow is active.

## Verified completed foundation
- Product overview, product specification and staged roadmap.
- NERDC source register and curriculum/term-allocation validation rules.
- PostgreSQL relational schema and migrations:
  1. `001_platform_hardening.sql`
  2. `002_identity_security.sql`
  3. `003_nerdc_curriculum_metadata.sql`
- Six subject records and three term labels are seeded by migration; no unverified lesson topics are seeded into the database.
- Flask health and catalogue endpoints, PostgreSQL repository and environment-variable example.
- API/database configuration unit tests and GitHub Actions workflow.
- Responsive student and admin interface prototypes.
- Latest catalogue integrity corrections committed: student dashboard subject count 5 → 6; term filter matches pending term-allocation metadata; student and API demo catalogues no longer assign unverified First Term or SS2 class placements; cards explicitly show class mapping pending; API tests assert the exact six-subject scope and pending class/term mapping; student UI contract tests protect the six subject tiles, dashboard count, pending-mapping labels, escaped catalogue rendering and correct preview record identity; admin UI contract tests protect workspace sections and the Channel-only manual announcement workflow.

## Not yet implemented
- Provisioned PostgreSQL database and application of migrations.
- Complete, verified NERDC topic mapping for SS1, SS2 and SS3 across the six subjects.
- Student registration/login, email verification/reset delivery, session lifecycle endpoints and production admin authorisation.
- Functional database-backed admin CMS and complete student portal workflows.
- Paystack checkout, server-side verification, webhook processing, refunds and entitlement fulfilment.
- Private audio storage, signed media delivery and playback.
- Teacher narration and two-presenter podcast scripts, generated audio and editorial approval.
- Telegram Channel creation/link and announcement publishing workflow. Initial publishing is intended to be manual; no bot automation is currently required.
- Production domain, privacy/terms/refund policies and support process.

## Testing and CI
- Historical GitHub Actions run `41342284699` passed.
- Historical run `41344517426` passed after the main six-subject groundwork.
- Later commits were not covered by those historical runs. The latest student rendering-safety and preview-identity tests require the next CI run to complete successfully before this expanded test suite is considered verified.

## Safety and release status
The student and admin interfaces remain prototypes. The API does not yet handle production accounts, payments, real student data or protected audio. No production database has been connected, no migrations have been applied, and no live service or legacy university bot has been changed or deployed.

Keep PR #1 in draft. Do not merge, deploy, spend money, or modify the legacy university bot without the owner's explicit approval.


## New requirements accepted: independent assessment and learner profiles

- Product requirement: students should independently register, learn, submit assessments, receive calculated scores and feedback, and see results without routine owner marking or one-to-one owner contact.
- Added `backend/migrations/004_student_profiles_and_assessments.sql` with learner profile metadata, explicit consent records, versioned assessment definitions/questions/attempts/answers, integrity events and notification records. This migration file was missing from the repository despite being referenced here; it has now been created and its schema contract tests added.
- Added `AUTOMATED_ASSESSMENT_AND_STUDENT_PROFILES.md` defining automated objective grading, result release, notifications, attempt integrity, student data minimisation and privacy requirements.
- Updated product journey to include learner profiles and automatic assessment results.
- Student frontend prototype now includes profile editing preview (display name, username, email, class, optional photo, bio, private-by-default visibility), assessment history and automated-results explanation.
- Added UI contract tests for profile fields, private default and assessment experience.
- Profile frontend is still a local prototype: it does not save data or upload images to a server.
- Migration 004 has NOT been applied to any database. There are no production registration, image upload, assessment submission, grading, result notification or background worker endpoints yet.
- Initial auto-grading scope is deterministic objective questions: single-choice, multiple-select, true/false, numeric with defined tolerance, and exact-answer text. Essays, handwritten work and open-ended proofs are not represented as reliably auto-gradable in the first release.
- No external reuse or marketing consent is bundled with account creation; optional use requires separate revocable consent. Profile visibility defaults to private. Because learners may be minors, legal/privacy and safeguarding review is a launch gate.

## Timed assessment and integrity requirements (specified; implementation pending)

- Added `TIMED_ASSESSMENT_AND_INTEGRITY_SPEC.md`.
- Timing policy: 36 seconds per question by default, with an explicit exception of 10 questions = 7 minutes. Examples: 5 = 3 minutes, 10 = 7 minutes, 50 = 30 minutes, 100 = 60 minutes.
- Each attempt requires a mandatory pre-test briefing and per-attempt affirmative agreement.
- Three qualifying focus/visibility/fullscreen incidents: warnings on incidents one and two; third incident ends the attempt and submits server-persisted answers.
- Browser restrictions are deterrents, not guarantees: a website cannot prevent screenshots, second devices, external cameras, or every OS/browser route. Integrity signals can false-positive; termination is flagged for review and appeal, not treated as conclusive cheating.
- Server-authoritative timer, answer persistence, immutable assessment versions, idempotent terminal states, objective grading, accessibility and minor-safety acceptance tests are specified.
- Added pure server-side timing helper `backend/assessment_policy.py` and unit tests `backend/test_assessment_policy.py` for the 36-second rule and invalid input handling. The helper now applies the approved 10-question/7-minute exception and tests cover the requested examples. These are policy primitives only; the live test service is NOT yet implemented.
- The new commits have not yet been confirmed by a completed CI run; do not treat them as passed until GitHub Actions reports success.

## Latest implementation caveat
The student and admin profile/assessment additions require a fresh GitHub Actions run to pass before the expanded test suite is considered verified.


## Student data isolation and extraction requirement

- Added `STUDENT_DATA_EXPORT_AND_ISOLATION_SPEC.md` defining per-student ownership boundaries, individual extraction, authorised class/subject/bulk extraction, privacy-safe fields, secure storage, auditability, expiry and acceptance tests.
- Added `backend/migrations/005_student_data_exports.sql` for export-job metadata and lifecycle audit events. The previously misplaced root-level copy has been removed so the ordered backend migration directory is canonical. It stores export metadata only; exported learner records remain in secured production storage, never in Git.
- Architecture decision: one immutable student UUID per learner, shared PostgreSQL with strict row-level ownership checks and indexed student foreign keys; no separate physical database per learner by default.
- Export APIs, permission model, background worker, private object storage, short-lived download links and automated tests are NOT yet implemented. Migration 005 has NOT been applied to any database.
- Corrected assessment time display for sub-minute tests (e.g. one question displays 36s rather than 0m 36s). The 10-question = 7-minute exception remains unchanged.


## Export-policy engineering increment
- Added `backend/export_policy.py`: validates individual/bulk export scope, UUID target, CSV/JSON format, SS1–SS3 filters, subject slugs and bounded date ranges; applies explicit field allowlists.
- Added `backend/test_export_policy.py`: covers invalid scopes/filters, date-range limits, duplicate filter normalisation and exclusion of password hashes/answer keys.
- These are policy primitives only. They do not provide authentication, admin authorisation, database queries, object storage, download URLs or a live export endpoint.
- GitHub Actions workflow runs Python unittest discovery from `secondary-school-platform/backend`; a new run is expected after these commits. Do not claim tests passed until the run completes.


## Identity-security engineering increment
- Added `backend/identity_policy.py` with bounded password validation and salted scrypt password hashing (Werkzeug), email normalisation, username validation, high-entropy one-time token generation with SHA-256 storage digests, and session-ID hashing.
- Added `backend/test_identity_policy.py` covering password hashing/verification, input bounds, email/username validation and token/session digest behaviour.
- These are tested identity primitives, not a working registration/login service. No account endpoint, email delivery, session cookie, CSRF protection, rate limiter or database identity transaction is claimed complete.
- No dependencies beyond the existing Flask/Werkzeug stack were added. Database migrations remain unapplied; deployment and production credentials remain owner-controlled.

- Latest branch head after the identity-policy increment: `73789c10375f25afb1ef91b1a4add69a18ca5fa1`. The workflow-run lookup did not return a run for this push, so the new identity tests are awaiting a confirmed CI result; do not report them as passed yet.


## Schema consistency correction
- Repository inspection found that migration 004 was referenced by the status document but absent from the actual file tree. Added `backend/migrations/004_student_profiles_and_assessments.sql` and schema contract tests in `backend/test_assessment_migration.py`.
- The migration adds private-by-default profile fields, explicit consent history, assessment definitions and objective question types, per-attempt briefing agreement and server deadlines, integrity events, answer persistence and notification records. It is not applied to any database.
- Moved the export migration into the ordered `backend/migrations/005_student_data_exports.sql` path and removed the misplaced root-level copy. Updated backend setup instructions to apply migrations 001–005 in order.
- Migration SQL and tests still require CI execution and a later real PostgreSQL migration rehearsal before any production use.
- Latest schema correction commits include `755f288` (migration 004), `cce8b62` (migration contract tests), `1158896` (canonical migration 005 path), `3c549e2` (remove misplaced copy), and `b4e0c2d` (migration setup instructions).


## Owner payment email notification requirement
- Owner alert destination is set to `emmanuelbjephter@gmail.com` by default through `PAYMENT_ALERT_RECIPIENT`.
- Added `backend/payment_notifications.py` with a minimal payment summary email builder and SMTP-over-TLS delivery. It fails closed if the mail relay is not configured and does not embed credentials.
- Added `backend/test_payment_notifications.py` for recipient, payment-summary validation, SMTP TLS path and missing-provider behaviour.
- Added SMTP and recipient variables to `backend/.env.example`; actual SMTP credentials must be entered privately as deployment secrets.
- IMPORTANT: this is notification infrastructure only. It is not yet called by a Paystack webhook. No live payment is being processed and no test email has been sent. Paystack signature/transaction verification, idempotent payment recording, durable outbox/retries and production SMTP configuration are still required before alerts are operational.
- ChatGPT's installed Gmail connector is separate from Learnwise's backend email sender. It can be used by ChatGPT to work with Gmail, but it does not grant the Learnwise server permission to send mail from that mailbox.


## Payment notification validation and migration documentation follow-up
- CI run `41351936842` on the previous head found one real validation gap: the alert builder accepted any three-letter currency, while the Learnwise product is currently NGN-only.
- Corrected `payment_notifications.py` to reject non-NGN currency values rather than treating a three-letter string as a valid currency.
- Corrected `backend/README.md` so the database setup sequence includes all five canonical migrations (001–005).
- The correction commits are `1be522b` (NGN validation) and `37d5a4e` (migration instructions). A fresh CI run is required; do not report the correction as passing until GitHub Actions confirms it.
- Payment alerts remain infrastructure only. No Paystack webhook, transaction verification, durable outbox, SMTP secrets, live email or live payment flow has been enabled.


## Paystack webhook security foundation
- Added `backend/paystack_webhooks.py` to authenticate Paystack's HMAC-SHA512 signature over the exact raw request body using constant-time comparison, then validate a minimal `charge.success` event (reference, positive integer amount in kobo, NGN currency, success status).
- Added `backend/test_paystack_webhooks.py` for valid signatures, modified bodies, invalid signatures, unsupported events, non-NGN currency, invalid statuses, malformed amounts and references.
- This is a security helper only, not a live webhook route. It does not call Paystack's transaction verification API, compare against a server-side order, persist events/payments, grant entitlements, or enqueue/send email. The payload alone must never authorise fulfilment.
- Updated backend README with the exact remaining verification and durable-outbox requirements. No Paystack credentials or live service settings have been added.
- CI confirmed success for the NGN validation and migration-documentation fixes: runs `41352701010` and `41352703175`. The status-documentation update also passed in run `41352709320`. Webhook helper/test CI is queued or running; wait for a completed run before calling it verified.


## Paystack verified fulfilment milestone (development only)
- Added `paystack_verification.py`: server-to-server verification through Paystack's transaction verification endpoint using a server-held secret; validates provider success, exact reference, exact expected kobo amount and NGN currency.
- Added `payments.py`: webhook orchestration authenticates the signed `charge.success` payload, finds the server-created Learnwise order, checks the amount, verifies the transaction directly with Paystack, then calls one atomic database fulfilment operation.
- Added `database.py` operations to look up an eligible pending order and atomically lock/check it, record success, grant the topic entitlement, record an idempotent webhook event, and enqueue an owner alert.
- Added migration `006_payment_notification_outbox.sql` for durable notification queue rows with dedupe keys, retry states and scheduling indexes.
- Added `POST /api/v1/webhooks/paystack`; invalid signatures return 400 and transient processing/database errors return 503 so the provider can retry. Added route and service tests.
- Corrected README setup to list all six migrations in order (001–006).
- The outbox delivery worker, retry/dead-letter execution, student authentication, secure server-side order creation, payment reconciliation operations and production deployment remain unfinished. The endpoint must not be advertised as production-ready or connected to live Paystack until those controls are implemented and reviewed.
- No real Paystack secret, SMTP credential, database connection, checkout, test email or production migration has been configured or executed.


## Payment email outbox worker
- Added `payment_outbox.py` with database-backed claim/lease using `FOR UPDATE SKIP LOCKED`, SMTP delivery outside the webhook request, stale-lease recovery, capped exponential retries (30 seconds to 1 hour), and dead-letter after eight failed attempts.
- Added unit tests for retry backoff bounds and attempt validation. Worker execution is not scheduled in a hosting environment; operators must configure and monitor a supervised worker before real payments.
- The webhook/outbox system remains development-only until CI passes on the latest branch head, server-side order creation and student identity are complete, and production configuration is reviewed.


## Student identity/session foundation (schema only)
- Added migration `007_student_sessions_and_rate_limits.sql`: server-side student sessions store only session and CSRF-token hashes, with expiry/revocation tracking; database-backed auth rate-limit buckets; and case-insensitive unique student email.
- Updated backend setup documentation to apply migrations 001–007 in order.
- Existing identity policy helpers support normalized email, username validation, scrypt password hashes, one-time token hashes and session-ID hashing.
- No registration/login/verification/reset route is active yet. No session cookies are issued. Auth service, CSRF enforcement, rate-limit operations, email verification delivery and account recovery remain to be implemented and tested before payment order creation can be enabled.
