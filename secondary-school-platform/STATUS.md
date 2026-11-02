# Implementation status

Last updated: 2026-11-02

## Current release status
- CI has passed on commit fa2a096: 148 unit/security tests, JavaScript syntax checks across six HTML pages, clean PostgreSQL 16 baseline plus migrations 001–013, PostgreSQL schema integration tests, assessment attempt/grade E2E, Paystack-shaped checkout/webhook/verification/entitlement idempotency E2E, and a non-publishing container build.
- Student account, private profile fields, published lesson catalogue, assessment attempt/history, issue reporting and private audio player are API-connected. Profile photo storage and visibility changes remain disabled.
- Admin login and the protected assessment review console are implemented. The older admin Studio remains a local prototype; full CMS, curriculum publishing and finance workflows remain unexposed.
- Private audio currently streams from a private local storage root using short-lived signed access cookies and entitlement rechecks. A production object-storage gateway, asset upload/scan pipeline and real audio assets remain outstanding.
- Docker image builds successfully; no image is pushed and no host/domain is configured. No production deployment or live database migration has occurred.
- NERDC acquisition is prepared but still requires authorised e-Curriculum access, permitted source capture, rights clearance and independent subject-teacher review. No topics have been fabricated or declared complete.
- Privacy notice and terms are draft templates. Nigerian legal review, DPIA, child/guardian assessment, safeguarding lead and release approval are mandatory before real learners are onboarded.
- Paystack end-to-end tests use synthetic data and provider-shaped stubs. No live/sandbox provider credentials are configured and no real payment was made.
- Draft PR #1 remains open and unmerged. Existing university bot @Ustpaymentbot remains untouched.

## External release gates
Authorised NERDC materials and permissions; subject-teacher verification; production-like backup/restore rehearsal; real Paystack sandbox credentials and test; private object storage; hosting and secret manager; independent security review; Nigerian privacy/legal and safeguarding sign-off; support and incident contacts; explicit owner approval for deployment.

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


## Verification checkpoint — 2026-11-01

- Current branch head: `0b5a70417844bfe78b5450b4a9d42cd6535c6885`.
- GitHub Actions run `41354575020` for this exact head completed successfully. Its API test job and all reported steps passed.
- The branch remains isolated from `main`; draft PR #1 is open, unmerged and still marked draft.
- This CI result verifies the automated suite on the current branch head; it does not validate a live PostgreSQL migration, production configuration, SMTP delivery, Paystack checkout or a deployed service.
- The next engineering milestone remains a complete, tested student identity service (registration, email verification, login/logout, session rotation/revocation, CSRF enforcement, rate limiting and password recovery). The existing identity helpers and migration 007 are groundwork only; no account endpoints or session cookies are active.


## Student identity service implementation increment — 2026-11-02

- Added `backend/identity_service.py`: PostgreSQL-backed student registration, normalized email/username, scrypt password hashes, hashed single-use verification and reset tokens, active-account login, server-side random sessions (only hashes stored), previous-session revocation on login, logout revocation, session expiry, CSRF-token hash validation, password reset with session revocation, and independent HMAC-keyed database rate-limit updates.
- Added `backend/identity_email.py`: SMTP-over-TLS verification and reset link delivery. Links require a configured HTTPS `PUBLIC_APP_URL`; raw tokens are not logged or returned by the public registration route.
- Added routes in `backend/app.py`: registration with explicit terms/privacy acceptance, email verification, login, authenticated current-student lookup, CSRF-protected logout, generic password-reset request, and reset completion.
- Added production cookie controls: HttpOnly session cookie, readable CSRF cookie, Secure in production, SameSite=Lax, and 12-hour expiry.
- Added `test_identity_routes.py` covering explicit consent, verification token non-disclosure, cookie attributes, unauthenticated access, and generic reset responses.
- Added required configuration keys to `backend/.env.example`: `AUTH_RATE_LIMIT_PEPPER`, HTTPS `PUBLIC_APP_URL`, policy versions, and existing SMTP settings.
- GitHub Actions run `41386067651` for exact branch head `320ab673ce888353a00ee54b6ebbbb643d42fe0a` completed successfully; all job steps passed. Earlier identity-service commits also passed.
- Important remaining limitations: this is not yet a production release. No PostgreSQL instance has been provisioned and migrations 001–007 remain unapplied; no real SMTP credentials or HTTPS app URL have been configured; no end-to-end test has exercised email delivery, concurrent database transactions, rate limits or session lifecycle against PostgreSQL. No browser registration/verification/reset screens have been connected to these API routes. Registration currently sends mail synchronously after account creation, so SMTP failure can leave a pending account requiring a future resend-verification workflow.
- Security review still required for proxy-aware client/IP throttling, email resend and abuse controls, CSRF/origin policy, production cookie/domain settings, database migration rehearsal, privacy/guardian-consent and safeguarding requirements for minors. Do not enable payments until identity and server-side order creation are complete and reviewed.


## Student account UI and assessment grading increment — 2026-11-02

- Added `frontend/account.html` with registration, sign-in, password-reset request/completion, email-verification handling, authenticated-session display and CSRF-protected logout. Dashboard now links to the account page.
- Identity emails now link to `account.html?action=verify|reset`; one-time token is removed from the browser URL immediately, and the page sets a no-referrer policy.
- Added account-page integration contract tests in `backend/test_account_ui.py`.
- Added `backend/assessment_grading.py` for deterministic server-side grading of single-choice, exact-set multiple-select, true/false, numeric-with-tolerance and exact-text alternatives. Multiple-select uses exact-set scoring; invalid grading definitions fail closed.
- Added `backend/test_assessment_grading.py`; CI run `41386305066` on commit `72df33f530ab07b119f012a47b30bf86cbba92dd` passed.
- Added migration `008_assessment_immutability.sql` with per-attempt question/answer-key snapshot columns and triggers preventing edits/deletion of published assessment/question records. Added static contract tests; CI run `41386340201` on commit `6cab3bd55f96d3f644f995b2645258e50e1d3e1d` passed.
- Updated backend README with migrations 001–008, identity configuration and grading/immutability boundaries.
- These are foundations, not a complete assessment system. No attempt-start service, server-authoritative attempt timer, question snapshot population, answer autosave, incident debounce/termination, atomic submission/grading persistence, appeals or result notifications have been implemented. No student-facing assessment execution is enabled.
- Current browser identity page assumes a same-origin API or reverse proxy; no CORS/cross-origin cookie configuration is provided. The deployed site must use HTTPS and a same-origin API arrangement.
- PostgreSQL and SMTP end-to-end verification remain pending; do not launch or accept payments until migrations are rehearsed, auth abuse controls and safeguarding are reviewed, and payment order creation is implemented.


## Assessment execution service increment — 2026-11-02

- Added `backend/assessment_attempts.py` with PostgreSQL-backed attempt creation, eligibility and attempt-limit checks, mandatory briefing acceptance/version, server UTC deadline creation, random question selection, immutable per-attempt question/answer-key snapshots, answer ownership/type validation and server-side answer persistence.
- Added student-facing routes for attempt creation, briefing acceptance/start, attempt retrieval, answer saving, submission and integrity events. Every route requires a valid student session and CSRF token.
- Server-side timing uses the approved 36-seconds-per-question rule and exact 10-question/7-minute exception. Browser time is not authoritative.
- Submission and expiry use deterministic objective grading and persist scores. First two debounced focus/visibility/fullscreen incidents warn; the third terminates the attempt and flags it for integrity review. The response explicitly does not treat an integrity signal as proof of misconduct.
- Added tests for answer-key omission from student question projections and timing-policy contracts.
- Updated backend README with the new endpoints and exact production limitations.
- This is a first execution-service increment, not a production-ready exam system. It has not been run against a real PostgreSQL instance. Appeal/fault-reporting, client autosave/recovery, result notifications, admin authoring, concurrency/idempotency hardening, and end-to-end browser tests remain. Database migrations 001–008 are still unapplied; no production service or student data is connected.
- Latest code changes require a new GitHub Actions run before they can be reported as CI-verified. Keep the draft PR open; do not deploy or enable live payments.


## Server-priced Paystack checkout increment — 2026-11-02

- Added `backend/payment_orders.py`: requires an active, email-verified student; loads the published lesson price from PostgreSQL; enforces NGN and the minimum ₦1,000 price; rejects existing entitlements; creates a server-generated payment reference/order; and initialises Paystack with the server-held secret.
- Added authenticated, CSRF-protected `POST /api/v1/topics/{topic_id}/checkout`. The amount is never accepted from the browser. Checkout URLs must use HTTPS and Paystack's checkout host.
- Added mocked provider tests for exact server amount/reference/currency, provider failure and untrusted redirect rejection.
- This is still not permission to accept real money. The DB has not been provisioned or migrated; Paystack secret is not configured; webhook/checkout has not been exercised end-to-end; outbox scheduling/monitoring, reconciliation/refunds, operational alerts, production security review and explicit launch approval remain outstanding.


## Private student profile API increment — 2026-11-02

- Added `backend/student_profiles.py` with authenticated read/update operations for display name, unique username and short bio. Email and class level are read-only through this endpoint; profile visibility remains private by schema default.
- Added `GET /api/v1/student/profile` and CSRF-protected `PATCH /api/v1/student/profile`. Updates are scoped to the authenticated student's UUID; unsupported fields (including class, email and photo storage) are rejected.
- Profile photo remains a local preview only; secure object storage/upload, export/download, deletion workflows and privacy-request processing are not yet implemented.
- Requires migration 004 and a dedicated PostgreSQL database. No live database is connected; real account/profile end-to-end testing and privacy/security review remain outstanding.


## Student assessment catalogue and test interface — 2026-11-02

- Added authenticated `GET /api/v1/assessments` listing only published assessments for the student's class and current availability window.
- Added `frontend/assessment.html`: loads eligible tests, lets the student choose an allowed question count, presents the mandatory briefing and unchecked agreement, starts only after acceptance, renders supported objective question types, saves answers through the authenticated API, displays the server-derived deadline, and submits on expiry or manual confirmation.
- The page requests fullscreen where supported and reports visibility, focus and fullscreen exits to the server. Copy/cut/paste/context-menu deterrents apply only during an active test; these cannot prevent screenshots, second devices or OS capture.
- Added UI contract tests to assert the test page uses CSRF, server deadline and integrity routes and does not embed answer keys.
- The browser page is an initial functional client, not yet browser/end-to-end tested against PostgreSQL. Mobile/accessibility testing, network retry queue for unsaved answers, explicit appeal/faulty-question forms, and result notifications remain.


## Revised NERDC curriculum architecture — 2026-11-02

- Owner preference confirmed: use the latest revised NERDC curriculum as Learnwise's target standard for SS1, SS2 and SS3.
- Added migration 009 for curriculum version records, cohort-specific applicability, source provenance/rights metadata, optional term assignments and evidence-gated topic publication. The target version key is `nerdc_ssec_2025`; cohort applicability is intentionally pending until official transition evidence is recorded.
- Added `backend/curriculum_import.py` and unit tests. Imports are restricted to the six selected subjects and target curriculum version. Publication is blocked without a traceable source section, named teacher review, approval timestamp, evidence note and known rights status. Official term allocation requires an official NERDC source; school term mapping requires a named school scheme.
- Added `CURRICULUM_IMPORT_TEMPLATE.csv` and `CURRICULUM_WORKFLOW.md` with NERDC source links, acquisition steps, rights safeguards and review workflow.
- Hardened the database-backed published catalogue: it now requires the target curriculum version, approved source record and explicit published curriculum review state. Unmapped/unsupported topics cannot silently enter the student catalogue.
- Current branch head before this checkpoint: curriculum work is committed on `secondary-school-platform-foundation`; latest Actions run for the prior head `c21921d` passed (run 41388502302). New curriculum commits require their own completed CI run.
- Migration 009 is not applied. No NERDC full-text material has been imported, no curriculum topic/term rows have been invented, and no external portal access controls have been bypassed. Official authorised documents and school schemes are still required for full content mapping.
- The branch remains separate from `main`; PR #1 remains open, draft and unmerged. No deployment, production database migration, payment activation or legacy bot change has occurred.


## Curriculum publication hardening — 2026-11-02

- Added migration 010 with a PostgreSQL trigger that independently blocks publication unless topic and curriculum statuses agree, the target revised NERDC version is active, the approved source matches class/subject/version, source and topic teacher-review evidence is complete, rights status is known, and term assignment is supported.
- Expanded the term-mapping constraint to support explicit `not_assigned` state. Unknown term placement cannot be silently stored as a term.
- Made migration 009's cohort-confirmation foreign-key creation repeatable.
- Added CSV import parsing and dry-run validation helpers. Learning outcomes are parsed as JSON arrays; malformed JSON is rejected with a line-specific error.
- Added tests for CSV import, invalid JSON, publication guard contract and term mapping states.
- CI passed for curriculum architecture/import commit `8d6475d` (run 41389078056). The migration 010 and CSV-import hardening commits are newer and awaiting their own CI result.
- Migrations 009–010 remain unapplied. No database has been connected or altered.


## Latest verification checkpoint — 2026-11-02

- Fixed the CSV test fixture after GitHub Actions identified incorrect CSV quote escaping. The parser was correctly rejecting the malformed test data.
- Latest branch head: `ba53e25ae0e353e2e848bdf522fb3f648e9ea11e`.
- GitHub Actions run `41389450150` completed successfully on that exact head (api-tests: success).
- Curriculum migrations 009–010 and CSV parser/dry-run validation now have passing automated tests. PostgreSQL execution/rehearsal remains outstanding because no dedicated database has been provisioned.
- PR #1 remains open, draft and unmerged. No deployment, live migration, payment activation or legacy bot change has occurred.


## Curriculum evidence immutability — 2026-11-02

- Added migration 011: curriculum source records cannot be updated or deleted while referenced by published topics; material changes to a curriculum version are blocked while published topics use it.
- Corrections must be captured as replacement source/version records and pass the review workflow rather than rewriting historical evidence.
- Added migration contract coverage for both immutability triggers.
- Migration 011 is authored but not applied. Trigger semantics and full migration ordering still require a disposable PostgreSQL rehearsal; CI must pass on the exact resulting branch head.


## Assessment reporting and appeals — 2026-11-02

- Added migration 012 for student assessment issue reports, including integrity appeals, question errors and technical problems.
- Added authenticated, CSRF-protected report submission and student-owned report listing endpoints. Question references are checked against the attempt; integrity appeals are restricted to integrity-terminated attempts; five-report cap per attempt.
- Added input-validation tests. Staff review queue, notification, appeal adjudication policy and operational response process remain outstanding.
- Migration 012 is authored but unapplied. PostgreSQL integration tests remain outstanding. GitHub Actions run 41391411324 passed on exact branch head `8f03d86c3d72843d45ace3b0a10c05529822830b`.


## Safe export serialization increment — 2026-11-02

- Added `backend/export_serialization.py` for allowlist-only CSV/JSON serialization, date/UUID/decimal normalisation, unsupported-value rejection and spreadsheet-formula injection protection.
- Numeric values remain numeric in CSV output; untrusted text beginning with formula characters is neutralised.
- Added tests for allowlist exclusion, nested metadata, date/decimal handling, malicious formula cells and invalid records.
- This is a serialization layer only. It does not expose student records, create an export endpoint, or replace the pending admin authorisation, audit, secure storage, expiring download, deletion and retention controls.
- Updated backend setup instructions to include migrations 001–012. No migration has been applied.


## Assessment report concurrency hardening — 2026-11-02

- Assessment issue submission now locks the owning attempt row before checking the per-attempt report count and inserting. Concurrent submissions for one attempt are serialised, preventing parallel requests from bypassing the five-report cap.
- Question references are parsed and canonicalised as UUIDs before database access; malformed identifiers and unhashable issue types return controlled validation errors rather than database exceptions.
- Added regression tests for UUID validation, malformed issue types and the row-lock contract.
- This does not yet create a staff adjudication workflow or admin endpoint. No admin access is exposed until role authentication and audit controls are implemented.


## Least-privilege admin policy increment — 2026-11-02

- Added `backend/admin_policy.py` with a default-deny capability matrix for owner, editor, reviewer, support and analyst roles.
- Added tests covering role boundaries, inactive/unknown principals, unknown capabilities and malformed inputs.
- No admin endpoint consumes this policy yet. Verified admin authentication/session management, principal loading, audited action wrappers and role-management controls are still required before exposing privileged routes.


## Latest engineering increment — admin security foundation

- Added migration 013: dedicated admin sessions store only session/CSRF hashes and record expiry, revocation and last-seen timestamps.
- Added partial active-session and expiry indexes; added normalised admin-email unique index.
- Added database trigger that rejects audit-event updates/deletes; corrections must be appended as new events.
- Added migration contract tests for hash-only storage, expiry/revocation, append-only audit and normalised email lookup.
- This is a database foundation only. Admin authentication routes, session service, capability enforcement, audit wrappers and controlled owner provisioning remain unimplemented; no admin route is enabled.
- Latest branch head before this increment: 26a1e67680b7e5b67d629371445c28128a5ed6da; CI passed on that exact head. New commits require a fresh exact-head CI run.


## Admin authentication increment

- Implemented database-backed admin login for offline-provisioned accounts, with HMAC-keyed rate limiting.
- Added 8-hour server-side sessions, hashed session/CSRF tokens, prior-session revocation, active-account checks, CSRF validation and logout.
- Added admin login, current-session and logout routes; session cookies use HttpOnly and SameSite=Strict, with CSRF header validation for logout.
- Added an audit append helper and unit tests for CSRF and audit metadata validation.
- No public admin signup, role assignment, password reset or privileged business endpoint is enabled. Capability enforcement and audit wrappers must guard each future admin operation.

## Release-readiness foundations added (2026-11-02)
- Added a PostgreSQL 16 disposable CI service and migration rehearsal runner. It loads the baseline schema, applies numbered migrations in order, records SHA-256 checksums and refuses remote/default database targets. A clean PostgreSQL replay is now part of CI; initial failures exposed and corrected the curriculum migration's PL/pgSQL delimiter and missing baseline-schema step. Latest replay is pending CI confirmation.
- Added a non-root Gunicorn Docker image and local PostgreSQL rehearsal compose file; no hosting provider or production deployment is configured.
- Connected the student lesson catalogue to the published API while preserving an explicitly labelled preview fallback. Fixed the password-reset query handler in the account page.
- Added an authenticated admin assessment-review page using admin session cookies, CSRF protection and role-gated review endpoints.
- Added HMAC-signed, short-lived private-audio authorisation primitives and test coverage. This is not yet an object-storage streaming endpoint; a private storage adapter and entitlement lookup are still required.
- Added NERDC acquisition, content production, privacy/safeguarding/legal review, secure audio and deployment/operations runbooks.
- Added automated unit/security tests for the new release foundations. External NERDC access/rights, independent teacher review, Nigerian legal sign-off, live provider credentials, staging infrastructure, real Paystack sandbox E2E and production approval remain external gates.
