## Current execution checkpoint — 8 November 2026, 18:50 WAT

**Project:** Think Tank senior-secondary learning platform.  
**Development branch:** `secondary-school-platform-foundation`  
**Current branch head before this documentation update:** `112f15f764299639763471f7813aea776a334358`  
**PR #1:** open, draft, unmerged; base `main` remains at `5d6d93ceec31ff3eb6851d567e4d61f7477bc492`.  
**Render staging:** `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`), latest deploy `dep-dbob0qh5efls73dc3tg0`, status `live`, deployed commit `97f243d3a1daea2ad910f59c405066ab75484955`. Auto-deploy is off; Free plan, Frankfurt.  
**Neon staging:** project `learnwise` (`spring-cloud-84267029`), branch `think-tank-staging` (`br-still-cherry-baz7g5hk`), state `ready`.  
**Exact-head CI:** workflow run `42505261079` passed all three jobs on the branch head: API/security and PostgreSQL tests, non-publishing container build, and public staging health. Health job log confirms HTTP 200 and JSON `status=ok`, `mode=database`, `service=secondary-school-api`.  
**Live browser acceptance:** read-only run `42505118340` passed 10/10 after the latest staging safety deployment. It is anonymous/read-only acceptance, not authenticated student acceptance.

### Current staging alignment

The seven commits between the Render deployment commit and the branch head contain documentation and the staging browser-acceptance specification only; the compare result contains no backend/frontend application runtime files. Therefore the currently deployed application code remains aligned with the branch's application code, and no redeploy is needed for those documentation/test-only changes. Render auto-deploy remains disabled.

### Database and storage audit

- Neon migration history contains 21 entries, versions 001–021. Migration 021 `021_synthetic_qa_identity` has source blob SHA `f7a08dc396534ee7bb8be25d656bf49415ba862e`, matching the current branch file.
- Read-only staging counts: 0 students, 1 active administrator, 6 subjects, 0 topics, 0 curriculum source records.
- Both `learnwise-private-audio` and `think-tank-private-exports` are private and currently contain no objects.
- Neon branchable storage is enabled. The existing `learnwise-render-staging-storage` credential has branch-scoped `storage:read` and `storage:write` capabilities; it is not bucket-scoped.
- No managed Neon snapshots are listed. The separate backup branch exists and is `ready`, but a managed restore drill and approved RPO/RTO remain outstanding.
- R2 control-plane synthetic upload/retrieval/checksum/deletion and anonymous public-access denial (HTTP 401) were previously verified. The Render application's configured S3 credentials have not yet passed the in-runtime diagnostic. Neon private-audio data-plane acceptance also remains outstanding.

### Identity, email and live acceptance

- Public student registration remains disabled.
- Synthetic QA issuance is deliberately disabled pending verified SMTP delivery and a dedicated controlled mailbox. No synthetic student exists.
- The owner-only private storage diagnostic remains available at `/admin/operations`; it must be run from the authenticated owner session. It tests synthetic audio and R2 object upload/retrieval/SHA-256/unsigned denial/deletion without learner data.
- The previous administrator email test returned `smtp_diagnostic_unavailable` (HTTP 503). Render logs contain redacted diagnostic failures and do not expose provider details. The current application route records only a bounded failure phase and exception class; SMTP delivery is not passed.
- Authenticated live browser acceptance therefore remains blocked until email delivery works, the synthetic invitation is issued and verified, and the temporary QA account is used for a controlled test.

### Release gates still open

1. Brevo sender/SMTP credential and real delivery/account-recovery verification.
2. Render-runtime R2 and Neon audio object-level acceptance; actual protected audio playback additionally requires an approved lesson asset and entitlement.
3. Paystack sandbox credentials and a controlled transaction/webhook/reconciliation test; live payments remain disabled.
4. Authorised NERDC curriculum source/licensing and qualified teacher review of the 18 SS1–SS3 × six-subject mappings.
5. Safeguarding lead, verified guardian consent, NDPA/DPIA, retention and processor/cross-border review, and Nigerian legal sign-off.
6. Managed backup restoration, approved RPO/RTO/retention and recovery drill.
7. Named monitoring/on-call recipient and successful alert delivery/incident drill.
8. Second authorised administrator and independent security review.

**Release decision: NOT READY for public student onboarding or production.** Keep PR #1 draft/unmerged; keep `main` untouched; keep registration, export worker and live payments disabled. No production deployment, paid upgrade, domain purchase, live payment, destructive action or real learner-data operation is authorised.


---

# Current execution checkpoint — 2026-11-03 (supersedes older historical status below)

**Development branch:** `secondary-school-platform-foundation`  
**Latest deployed code commit:** `78edbd9e125e9f26cbb4b2ae846117a90a00deee`  
**Latest test/documentation commit:** `76dbc6eeac7160bbfd5262b6e60f432d23da523b`  
**PR #1:** open, draft, unmerged. The current main head is `5d6d93ceec31ff3eb6851d567e4d61f7477bc492`; compare it with the branch before any future sync.  
**Staging API:** https://think_tank-staging-api.onrender.com  
**Render service:** `think_tank-staging-api`, Free plan, Frankfurt, Docker, one instance. Latest deployment is live on commit `0675b2f...`.  
**Neon project:** `think_tank` (`spring-cloud-84267029`), Free plan, PostgreSQL 16, Frankfurt.  
**Neon staging branch:** `think_tank-staging-rehearsal` (`br-still-cherry-baz7g5hk`).  
**Private audio bucket:** `think_tank-private-audio` (private, branch-scoped).  
**CI:** API tests and container-build checks passed on commit `76dbc6eeac7160bbfd5262b6e60f432d23da523b` (164 unit/security tests; two optional DATABASE_URL-only test classes skipped).

## Verified progress in this checkpoint

- Provisioned the dedicated Neon project and a separate staging branch; applied `DATABASE_SCHEMA.sql` and ordered backend migrations 001–013 to that branch.
- Added `think_tank_migration_history` with all 13 migration versions and source blob hashes. The database currently contains six subjects and three term labels; no student records or unverified topic mappings have been fabricated.
- Created a private Neon Object Storage bucket and branch-scoped S3 credentials. Credentials are stored in Render environment variables, not in Git or this document.
- Render now uses a separate `think_tank_app` database login, not the database owner. It has no superuser, create-database or create-role rights. Audit rows are append-only at the application role level; admin role changes are not permitted through the app role.
- Deployed the Flask API and student pages from one HTTPS origin. Routes cover the student home, account, lesson, assessment, stylesheet, admin studio, operations and assessment review pages.
- Added S3-compatible private audio retrieval and upload code, MIME/signature/size validation, pending-review state, entitlement-protected streaming, and separate editor-upload/reviewer-approval capabilities. No real lesson audio has been uploaded or approved.
- Added protected admin operational views for student records, payment summaries, curriculum source metadata and audio assets. Student/payment data is not exposed to unauthorised roles.
- Added a one-time owner-admin bootstrap script. No admin account has been created yet; there is no public admin registration.
- Configured the staging public URL and Brevo SMTP host/port. No Brevo account credentials or verified sender identity have been supplied, so real email delivery remains disabled.
- Explicit staging feature flags keep student registration and Paystack checkout disabled until SMTP, sandbox and safeguarding gates are cleared.
- Preserved the latest main-branch assessment/profile specification and root-level migration file. `MIGRATION_RECONCILIATION.md` explains why the backend migration sequence is canonical and why the older overlapping root migration must not be applied again.

## Free/low-cost architecture decision

- **Database + private files:** Neon Free. Current published Free limits include 1 GB Postgres storage and 100 CU-hours per project/month, plus 5 GB object storage. Keep compute at 0.25 CU and monitor usage. See https://neon.com/blog/neon-free-plan-1-gb-per-project.
- **API hosting:** Render Free for staging and early previews. Free services can sleep and have limitations; not suitable for a production SLA or dependable student exam sessions. See https://render.com/docs/free.
- **Transactional email:** Brevo Free is the preferred next provider because it includes 300 emails/day and transactional email. Verify a sender domain and add SMTP credentials only in Render's secret environment. See https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans.
- **Storage fallback:** Cloudflare R2 has a 10 GB-month free standard-storage allowance, 1 million Class A and 10 million Class B requests, with no egress charge. It requires R2 subscription activation; stay on Neon Object Storage for the initial 5 GB rather than enabling another service prematurely. See https://developers.cloudflare.com/r2/pricing/.
- **Payments:** keep Paystack. Standard Nigeria local processing is 1.5% + ₦100, capped at ₦2,000; the ₦100 is waived below ₦2,500. Paystack documents a lower education-institution rate, but eligibility must be confirmed with Paystack before relying on it. See https://paystack.com/pricing and https://support.paystack.com/en/articles/2130306.

## Important remaining gates

1. Create the first owner administrator using the secure bootstrap script from a trusted environment; remove its temporary environment variables immediately afterwards.
2. Create/verify a Brevo sender identity and place SMTP username/password in Render secrets; then test verification and password-reset emails.
3. Run real staging HTTP/browser tests across mobile/desktop, including student registration, email verification, assessments, payments sandbox and private audio upload/playback. CI tests are not a substitute for browser acceptance.
4. Configure Paystack sandbox credentials in Render secrets and test actual sandbox checkout, webhook delivery/retries, refunds and reconciliation. No real payment has been processed.
5. Populate and verify the 18 SS1–SS3 × six-subject curriculum combinations from authorised NERDC materials, with independent qualified teacher sign-off. No curriculum topics have been invented.
6. Complete Nigerian privacy/legal review, DPIA, child/guardian consent assessment and safeguarding approval before real learner data.
7. Configure monitoring/alerts, backup and timed restore evidence; add a custom domain only if/when owner approves.
8. Inspect the two commits newly added to `main` before any branch sync. Main has not been modified by this work.

**Release decision: NOT READY for public student onboarding or production.** Staging code and infrastructure are live, but external credentials, verified curriculum, formal approvals and real end-to-end acceptance remain outstanding. Keep PR #1 draft and unmerged. Do not deploy production, activate live payments, buy paid resources or merge without owner approval.

---

# Current execution checkpoint — 2026-11-02 (supersedes historical status notes below)

**Branch:** `secondary-school-platform-foundation`  
**PR:** #1 remains draft, open and unmerged.  
**Latest commit at this checkpoint:** `83db267f71dbcbe4bd4bd28db222d032668a7c66`  
**CI:** GitHub Actions run 41403318357 (push) and 41403324273 (pull request) both completed successfully on this exact commit.  
**Run:** https://github.com/JephterAce/Year-1-Tutorial/actions/runs/41403318357

## Current verified engineering position

- The repository audit is recorded in `EXECUTION_AUDIT.md`.
- The branch includes a Flask API with student registration/email verification/login/logout/password reset, private profile, published catalogue, assessment execution/history/reporting, server-priced Paystack checkout/webhook verification, admin authentication and assessment issue review, and protected private-audio access routes.
- Student pages include catalogue/dashboard, account/profile, lessons/audio player and assessments. Admin pages include a local Studio prototype and protected assessment-review workspace.
- Migrations 001–013 are present. CI on the current commit passes unit/security tests, frontend/admin JavaScript syntax checks, disposable PostgreSQL 16 baseline plus ordered migration replay, PostgreSQL schema integration, assessment/payment database E2E using mocked provider responses, and non-publishing container build.
- Direct `python app.py` startup registration ordering was corrected in commit `c62354310d9252d8b1e2d69ae1ac7ffcbe2bcc34`; its CI passed. The audit record and this checkpoint were then committed in `83db267`; its CI also passed.
- The admin assessment-review Blueprint is registered in `app.py`; review routes enforce authenticated admin sessions, CSRF, capability checks and append-only audit records.

## Not complete — external or real-environment gates

- No managed staging PostgreSQL instance has been provisioned or connected. CI PostgreSQL is disposable and is not a deployment database.
- No real SMTP account is configured; email verification/reset must be tested end-to-end with a controlled mailbox.
- No Paystack sandbox credentials or real sandbox transactions/webhook deliveries have been supplied or run. CI uses mocks.
- Private audio has a local private-storage implementation; approved cloud object storage, upload/scan pipeline and real approved audio assets are not configured.
- NERDC source rights/access, authorised curriculum corpus, 18 class-subject evidence sets and independent teacher verification remain outstanding.
- Nigerian legal/privacy review, DPIA, child/guardian assessment, safeguarding lead and formal approval remain outstanding.
- No hosting account, staging domain, secret manager, monitoring/alerting or backup/restore evidence exists.
- No real student data should be entered until required privacy/safeguarding approvals and staging controls are complete.

## Release decision

**NOT READY for public student use or production.** The repository and CI foundation are verified; external integrations, approvals and real staging acceptance remain release blockers. Keep PR #1 draft/unmerged. Do not deploy, apply migrations to a live DB, activate payments, purchase services or alter production secrets without the owner's explicit approval.

---

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
- ChatGPT's installed Gmail connector is separate from Think Tank's backend email sender. It can be used by ChatGPT to work with Gmail, but it does not grant the Think Tank server permission to send mail from that mailbox.


## Payment notification validation and migration documentation follow-up
- CI run `41351936842` on the previous head found one real validation gap: the alert builder accepted any three-letter currency, while the Think Tank product is currently NGN-only.
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
- Added `payments.py`: webhook orchestration authenticates the signed `charge.success` payload, finds the server-created Think Tank order, checks the amount, verifies the transaction directly with Paystack, then calls one atomic database fulfilment operation.
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

- Owner preference confirmed: use the latest revised NERDC curriculum as Think Tank's target standard for SS1, SS2 and SS3.
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


---

## Current verified checkpoint — 7 November 2026

**Development branch head:** `905171f7a55254887c9cc905449598bc96403a58`

**CI:** Exact-head push run [42412752132](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42412752132) and PR run [42412756438](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42412756438) passed. Coverage includes unit/security, JS syntax, all 17 migrations on disposable PostgreSQL, schema integration, assessment/payment E2E, synthetic student registration-to-results journey and container build without publishing.

**Newly implemented**
- Student progress page now consumes the authenticated dashboard API and displays lesson completion, practice/assessment totals, graded average, per-subject progress and recent lesson activity.
- Student podcast library now lists only episodes with an active student entitlement, published topic, approved audio asset and approved linked podcast script. Playback uses short-lived private audio authorization.
- Added unit, route-auth and UI wiring tests.

**Provider state (read-only)**
- Render staging remains live on old deployed commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`; no new deployment was triggered. Auto-deploy is off.
- Neon staging remains ready with 13 migrations, 6 subjects, 0 topics, 0 students, 1 administrator and 6 audit events. Private audio bucket exists and is empty.
- Repository migrations 014–017 are CI/rehearsal verified but not applied to managed staging. Do not deploy the new code to staging until migration/deployment prerequisites and owner approval are satisfied.

**Still not production-ready:** no approved curriculum corpus/rights and teacher sign-offs, no published topics, no podcast assets, no real SMTP delivery proof, no Paystack sandbox acceptance, no private audio provider E2E, incomplete CMS/assessment authoring and admin UAT, incomplete privacy/child safeguarding/legal approvals, and no backup/restore, monitoring or independent security sign-off.

**Protected boundaries:** PR #1 remains draft/open/unmerged; main and legacy university bot untouched; registration and checkout disabled; no production deployment or live payment authorized.


---

## Verified update — 7 November 2026 (podcast access hardening)

Development head: `090438017e7b326c2327a995036278c3bb90ea8e`.

Exact-head CI passed on push run [42412897995](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42412897995) and PR run [42412902759](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42412902759). Both passed unit/security, frontend/admin JavaScript syntax, all 17 disposable PostgreSQL migrations, schema integration, assessment/payment E2E, synthetic registration-to-results journey and non-publishing container build.

The student progress dashboard and podcast library are implemented. Podcast listing and private playback require an active entitlement, a published topic, approved audio and an approved linked podcast script. Direct audio access independently enforces script approval. No permanent object URL is exposed.

Render has not been updated; latest live deployment remains `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`. Neon managed staging remains at 13 migrations, 6 subjects, 0 topics, 0 students, 1 administrator and 6 audit events; private audio bucket is empty. Migrations 014–017 are not applied to managed staging.

The platform is not production-ready. Curriculum rights/content, teacher review, SMTP/Paystack sandbox, private audio provider E2E, full CMS/admin/student UAT, privacy/child safeguarding/legal approvals, monitoring, backup/restore, independent security review and production authorization remain open. PR #1 remains draft/open/unmerged; main and the legacy bot remain untouched.


---

## Verified update — 7 November 2026 (assessment history UX)

Application commit `199c4e52bfd86050df4058a50593846745434fbd` passed exact-head push CI [42413078275](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42413078275) and PR CI [42413082270](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42413082270).

Assessment history now displays accurate attempt counts, score fraction, question count, percentage, pass/fail, integrity-review status and submitted/started time. The source is the existing authenticated assessment-history API. Added UI regression coverage.

Progress dashboard and approved, entitlement-gated private podcast library remain implemented. Managed staging has not been deployed or migrated; it still has 13 migration records while repository CI verifies 17 migrations on disposable PostgreSQL. Render remains on its previous live commit. The project is still not approved for production.


---

## Verified update — 7 November 2026 (saved lessons)

Application commit `8e1f838c34d5dcc55c6358e74c97928566dcb622` passed exact-head push CI [42413332222](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42413332222) and PR CI [42413335065](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42413335065).

Saved lessons are now database-backed through migration 018, with authenticated list, CSRF-protected save/remove routes, idempotent bookmarks, published-topic validation and a working student UI. Schema integration checks now account for the baseline plus 18 numbered migrations.

Managed Neon staging still has only 13 migration records; migrations 014–018 have not been applied there. Render staging has not been deployed and remains on its previous live commit. No production or live payment action occurred. The platform is not production-ready.


---

## Verified update — 7 November 2026 (admin authoring, finance, data rights and release operations)

### Code verification
- Latest fully tested application commit: dd7b620676c4312aa9540a89d19be71381f71ec5.
- Exact-head push CI [42415624459](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42415624459) and PR CI [42415628254](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42415628254) passed.
- Passed 241+ unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL replay of baseline plus migrations 001–019, schema integration, assessment/payment E2E, synthetic registration-to-results, authenticated and anonymous Playwright browser journeys, and non-publishing container build.
- Playwright uses a disposable PostgreSQL database, synthetic owner admin and synthetic subjects. No managed staging student accounts or payments were created.
- A browser test first caught an async form handler bug (event.currentTarget became null after await); the handler now captures the form before asynchronous work. A later browser assertion was corrected to check the selected assessment title. Exact-head browser CI now passes.

### Implemented
- Improved admin mobile navigation, skip links, focus visibility, reduced-motion and forced-colour support; student account fields now have accessible labels/autocomplete.
- Added a protected assessment authoring workspace and role-gated API: list/detail, create draft, validated objective questions (single choice, multiple select, true/false, numeric, exact text), answer-key-safe detail projection, and immutable publication.
- Added read-only finance ledger summary and exception indicators; no Paystack calls/refunds are initiated from this view.
- Added student self-service JSON export, privacy request intake/history/withdrawal and administrator data-rights review queue. Deletion is intake-only and never auto-erases data.
- Added migration 019_student_data_rights_requests.sql.
- Added SMTP transport contract tests with mocked STARTTLS/SSL, retained Paystack verification contract tests and private S3-compatible audio/range/revocation tests.
- Added guarded local backup/restore rehearsal script and backup/recovery/monitoring runbook.
- Updated migration reconciliation and release-gate documentation.

### Migration and managed provider state
- Repository canonical sequence is baseline plus numbered migrations 001–019 (20 history entries in CI).
- Managed Neon project learnwise, branch think-tank-staging (br-still-cherry-baz7g5hk), has exactly 001–013 in learnwise_migration_history; counts remain 0 students, 1 admin, 6 subjects, 0 topics, 6 audit events.
- The separate think-tank-migration-rehearsal-20261106 branch also has only 001–013. Do not mistake it for a rehearsal of 014–019.
- Migrations 014–019 passed disposable CI but are not applied to managed staging.
- Render service learnwise-staging-api has auto-deploy off. Latest live deployment is dep-dbn2dcrl550s73f9ahag, commit 0f343fff800b619fdaff76f5ee97225ec6c3dbdf, completed 2026-11-06T19:13:13Z. No deployment was triggered.
- Public /health could not be directly verified in this run: web open returned “URL is not accessible by this tool”; Render HTTP request metrics for host learnwise-staging-api.onrender.com, path /health, last-hour default range returned no data. This is unavailable evidence, not a confirmed health failure. Render service metadata has no configured healthCheckPath.

### External and release blockers
- SMTP code is tested with mocks; no live provider delivery/account recovery proof or controlled mailbox.
- Paystack verification contracts pass; no authorised Paystack sandbox account/keys and no real sandbox charge/webhook/refund acceptance.
- Audio storage/range/security logic is tested with mocks; managed bucket learnwise-private-audio remains empty and no real provider playback/revocation acceptance exists.
- No authorised NERDC corpus/licence or qualified teacher approvals.
- No completed guardian identity/consent verification, NDPA/DPIA, retention schedule, safeguarding/legal sign-off or processor/cross-border review.
- Backup/restore procedure exists but no managed backup restore has been executed; RPO/RTO and retention are not approved.
- Monitoring/alert delivery and independent security review remain outstanding.
- Full bulk-export worker, large streamed exports, private export archives, signed URL lifecycle and actual data deletion workflow remain outstanding.
- PR #1 remains open/draft/unmerged. Main and legacy university bot remain untouched.

### Current release state
**Development software milestone substantially advanced; staging and production release are not approved.** Do not apply migrations 014–019 or deploy code until the owner approves a reviewed staging migration/deployment plan, backup and rollback evidence. Production launch requires a separate explicit approval after all legal, safeguarding, curriculum, payment, audio, security and operational gates pass.


---

## Verified update — 7 November 2026 (authenticated student data-rights browser acceptance)

- Latest fully tested application commit: a057289c4930b86b6bdd5176bd71e61a9536f044.
- Exact-head push CI [42416064502](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416064502) and PR CI [42416068375](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416068375) both passed.
- The unit/security suite passed 246 tests. Python compileall, frontend/admin JavaScript syntax and guarded backup script shell syntax passed.
- Disposable PostgreSQL replay of baseline plus migrations 001–019, schema integration, assessment/payment E2E and synthetic registration-to-results all passed.
- All 14 Playwright tests passed. New authenticated student browser journey signed in as a synthetic student, submitted and withdrew a privacy request, downloaded the student's own JSON export, and verified the export omitted password hashes, answer keys and provider payloads. Admin assessment creation/publication and admin data-rights queue journeys also passed.
- All fixtures were synthetic and isolated to the ephemeral CI database. No managed staging student account, payment or media object was created.
- The browser test caught and fixed another asynchronous form issue: the student privacy-request form now captures its form element before awaiting the API response.
 

### Additional migration reconciliation evidence — 7 November 2026
- Queried managed staging migration history including source_blob_sha and compared all recorded versions 001–013 against the development branch's GitHub blob SHA for each canonical backend migration.
- Result: 13/13 applied migration source blobs match exactly. This confirms no source checksum drift among the currently applied migrations.
- Migrations 014–019 remain unapplied to managed staging. Their clean disposable CI replay does not replace a staged upgrade rehearsal from the actual 001–013 state.


---

## Verified update — 7 November 2026 (public health, backup restore and provider reconciliation)

- Current development branch head: ee2cc4306279772ecb05a3813eb33266c134d497.
- Exact-head push workflow [42416698937](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416698937) and PR workflow [42416702456](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416702456) both passed.
- The workflow now performs a read-only public Render health check on every push/PR run. Latest result: HTTP 200; JSON status=ok, mode=database, service=secondary-school-api. These fields match the previously recorded healthy response; no health regression detected.
- Full workflow also passed 246 unit/security tests, Python compileall, JavaScript and shell syntax, baseline plus migrations 001–019 replay, local logical backup/restore to a separate disposable PostgreSQL database (restored 20 migration-history entries), schema integration, assessment/payment E2E, synthetic student journey, 14 authenticated/anonymous Playwright tests and non-publishing container build.
- Managed Neon applied migrations 001–013 remain source-checksum exact (13/13). Migrations 014–019 remain pending.
- Render latest deployment remains dep-dbn2dcrl550s73f9ahag, status live, SHA 0f343fff800b619fdaff76f5ee97225ec6c3dbdf, finished 2026-11-06T19:13:13.356Z. The current development branch is 225 commits ahead of that deployed SHA. No deployment was triggered; auto-deploy remains off.
- Render event history for the last seven days shows the latest build and deployment succeeded and no failure event. Service healthCheckPath remains empty; the new CI check provides public endpoint verification without changing Render configuration.
- The public health check is now verified by the GitHub runner; the earlier web-tool accessibility limitation is superseded for this run.


### Latest branch-head confirmation — 7 November 2026
- Current branch head is 1419ed4b8c6011ad5d30ea9299a36c2816e1aa3c. Changes after application commit a057289c4930b86b6bdd5176bd71e61a9536f044 are documentation/workflow evidence updates; no additional application code was introduced.
- Exact-head push [42416831355](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416831355) and PR [42416833832](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416833832) passed.
- Both exact-head runs passed the read-only public staging health job (HTTP 200, status=ok, mode=database, service=secondary-school-api), all unit/database/browser checks, and local backup/restore rehearsal.


### Final documentation-head confirmation — 7 November 2026
- Latest repository/PR head: 2098d7ad37b830a84a1120654afc56b5152ae4ef. This update contains documentation and PR-status evidence only; tested application code remains a057289c4930b86b6bdd5176bd71e61a9536f044.
- Exact-head push CI [42416959890](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416959890) and PR CI [42416965208](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416965208) both passed, including the public staging health job, backup/restore rehearsal and authenticated browser suite.


### Final handover pointer — 7 November 2026
The current development branch and open draft PR head is fc77dbc714af2103b50f58c02bff844556a776ad. Exact-head push workflow 42417089283 and PR workflow 42417094553 both passed. This head contains documentation/PR-status updates only; latest tested application code remains a057289c4930b86b6bdd5176bd71e61a9536f044. Public health is HTTP 200/status=ok/mode=database/service=secondary-school-api. No deployment or managed migration was performed.


### Latest verified continuation — 8 November 2026

- Render workspace Emmanuel's workspace was explicitly confirmed. The service learnwise-staging-api (srv-dbkqcmt9fdbs73c2kdpg) is live, free plan, Frankfurt, auto-deploy disabled, and still deployed at c5805a6fc463fd040e64e8223d58ed3dbf37d143. The 8 November deploy dep-dbo22jp5efls73cm1sb0 completed successfully; no further deploy was made.
- GitHub Actions staging-health verified the public endpoint at HTTP 200 with status=ok, mode=database, service=secondary-school-api. The latest Render logs show Gunicorn listening on port 8000 and Render reporting the service live.
- Managed Neon staging branch think-tank-staging contains migrations 001–019. All 19 recorded source_blob_sha values were compared with GitHub blob SHAs and match. Read-only counts: 6 subjects, 0 topics, 0 students, 1 active administrator, 0 data-rights requests.
- A backup branch think-tank-staging-backup-2026-11-08 and an isolated migration rehearsal branch think-tank-migration-rehearsal-2026-11-08 are ready. Migration 020_private_student_export_approval.sql was applied only to the rehearsal branch; all added columns, four check constraints, approver FK and queue index were verified. Its migration-history SHA matches the repository blob SHA. Managed staging remains at 019.
- Development-branch implementation now includes admin export request/approval/download routes, a restricted export UI, streaming repeatable-read worker, dedicated private-storage configuration, checksum manifest, short-lived signed URLs, expiry cleanup, request caps and two-person approval. Worker disabled; no export bucket, credentials or schedule provisioned. Subject-filtered bulk export is rejected safely. A second active owner approver is required; only one active admin exists.
- CI run 42459497431 included 258 tests. The health and container-build jobs passed; API tests failed on two test fixtures missing export_scope. Those fixtures were corrected in subsequent commits. No fresh exact-head CI result has yet been observed, so the new code is not certified as passing.
- The new application branch has not been deployed. PR #1 remains open/draft/unmerged; main and production remain untouched.

#### Remaining release blockers
SMTP/password recovery verification; Paystack sandbox E2E; private audio storage/playback acceptance; authorised NERDC materials and teacher review (zero topics in staging); child safeguarding/guardian consent/NDPA/DPIA; Nigerian legal review; managed backup restore/PITR and RPO/RTO; monitoring/incident-alert verification; independent security review; export bucket provisioning, second approver, scheduled worker and subject-scoped exports.

Production release remains blocked. Migration 020 and its matching code deployment require a fresh passing exact-head CI run, isolated upgrade evidence and explicit owner approval before staging promotion.


### Repository pointer — 8 November 2026
- Latest verified development-branch head before the final handover update: `c421b4e305731c8850b6b3bd93e856578fbbd27c`.
- The branch is 30 commits ahead of the deployed Render SHA `c5805a6fc463fd040e64e8223d58ed3dbf37d143`; it is not deployed.
- PR #1 remains open as a draft and unmerged. The current GitHub connection returned no fresh exact-head workflow run/status for this head. The last relevant run `42459497431` had passing health and container-build jobs but a failing API test job; the two missing test-fixture fields were corrected afterward, and a fresh run is still required.


### CI correction checkpoint — 8 November 2026
- Workflow run 42460006986 at branch commit 1316c1d2fa789c2f67eb389ac10605f0489ac374 passed all 260 unit/security tests, the public staging-health job (HTTP 200/status=ok/database/secondary-school-api) and the non-publishing container build.
- The Python/JavaScript/shell syntax step then failed because the new exports admin page contained a literal escaped newline in its inline script. This was corrected in commit 81d33094f0506a71c9f72984133075fa75c84252; a read-back confirms the page now contains a real newline. No fresh exact-head workflow result is yet available, so migration replay, backup restore, PostgreSQL integration and browser acceptance remain unverified for this corrected head.
- Current branch head at this checkpoint: 81d33094f0506a71c9f72984133075fa75c84252; 54 commits ahead of deployed Render SHA c5805a6fc463fd040e64e8223d58ed3dbf37d143. PR #1 remains open/draft/unmerged; no deployment was triggered.


### Green CI checkpoint and new export-browser run — 8 November 2026
- Workflow run 42460191786 (run 1180, commit 7de9dd1d0da160e634673fc813a16befb147e383) completed with all three jobs successful: API tests, staging health and container build. Its API job passed 260 unit/security tests, syntax checks, all 20 migration replays/idempotency, local backup/restore, PostgreSQL schema integration, assessment/payment E2E, registration-to-results and the existing authenticated/anonymous browser suite.
- A second run 42460225765 (run 1184, commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) includes the new export request/cancel/self-approval browser test and anonymous /admin/exports redirect check. At the latest inspection, unit/security, syntax, migration replay, backup/restore, PostgreSQL integration, assessment/payment E2E and student journey all passed; Playwright installation/browser acceptance was still in progress.


### Full exact-code CI pass — 8 November 2026
- Workflow run 42460225765 (run 1184, tested code commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) completed with all three jobs successful: api-tests, staging-health and container-build.
- All 260 unit/security tests passed; Python, admin/frontend JavaScript and shell syntax passed; all 20 numbered migrations replayed and replayed idempotently; backup/restore rehearsal passed; PostgreSQL schema integration passed; assessment/payment E2E passed; registration-to-results passed; anonymous and authenticated Playwright acceptance passed, including the new admin export request/cancel flow and requester self-approval prohibition.
- The workflow also verified staging health HTTP 200, status=ok, mode=database, service=secondary-school-api. The container was built but not published.
- The tested code commit is an ancestor of the current branch; subsequent commits only update project records. The new code is still not deployed to Render. Migration 020 remains only on the isolated rehearsal branch.


### Final repository reconciliation — 8 November 2026
- Latest tested application-code commit: `5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3`, fully green in workflow 42460225765 (run 1184).
- Current branch head before this final status/handover update: `3a5cace1db3b9de2803b18f22c4974e69c4b963d`; it is 8 documentation-only commits ahead of the tested application-code commit. No application code changed after the green run.
- Render remains live on `c5805a6fc463fd040e64e8223d58ed3dbf37d143`, auto-deploy off. Managed Neon remains at 19 migration records. Migration 020 remains only on isolated rehearsal branch `br-divine-bread-bah58gvn`.
- PR #1 remains open, draft and unmerged. Production remains blocked.


### Managed staging migration 020 and Render staging deployment — 8 November 2026

- Owner explicitly approved applying migration 020 and deploying the tested application code to staging only. No production, main-branch, or PR-merge action was authorised or performed.
- Managed Neon project `spring-cloud-84267029`, branch `think-tank-staging` (`br-still-cherry-baz7g5hk`), database `learnwise`: migration history now contains 20 entries; latest is `020_private_student_export_approval`. Recorded source blob SHA `3ee86c0d909f429f6ca5787c47b51f86dfdf9a13` matches the canonical GitHub migration file. Verified all six new columns and all four new constraints are present.
- Render service `learnwise-staging-api` deployment `dep-dbo2l1h5efls73cnf8j0` is `live` on branch `secondary-school-platform-foundation`, commit `c03b7e98aee4a046d300185eb5089b42f747a75c`. Build succeeded; Gunicorn started and worker processes booted. Service auto-deploy remains off; this was a manual staging deploy.
- The deployed code commit is documentation-head `c03b7e9...`; application code remains the exact fully CI-tested commit `5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3`, with only documentation changes after it.
- Live public `/health` HTTP response and authenticated browser acceptance have NOT yet been independently confirmed from this execution environment: the web fetch could not access the Render endpoint and outbound DNS resolution from the container failed. Render deployment status and process startup are verified, but they are not substitutes for an HTTP 200 health response or a real authenticated browser session. The CI health and synthetic Playwright tests remain green on the tested application commit.
- The isolated migration-rehearsal branch remains separate; managed staging now has migration 020 applied. No owner-admin bootstrap was rerun. Export worker remains disabled; no private export bucket/credentials or schedule were provisioned.

#### Remaining release blockers
SMTP delivery/password recovery; Paystack sandbox E2E; private audio provider playback acceptance; licensed NERDC content and teacher sign-off; child safeguarding/guardian consent/NDPA/DPIA; Nigerian legal review; managed backup restoration/RPO/RTO; monitoring and alert delivery; independent security review; second active owner administrator; private export bucket and worker scheduling. Staging is not production-ready.


### Owner-confirmed live staging health — 8 November 2026
The owner opened `https://learnwise-staging-api.onrender.com/health` after deployment and returned the live JSON response `{"mode":"database","service":"secondary-school-api","status":"ok"}`. Public staging health is therefore verified after deployment. Authenticated browser acceptance against the deployed service remains outstanding.


### Release-gate execution audit — 8 November 2026

This checkpoint records the latest connected-provider inspection and the owner's live admin-page confirmation. It supersedes earlier statements that migration 020 or the live admin exports page had not yet been verified, but it does not clear the external release gates below.

- **Live admin acceptance:** owner confirmed that the authenticated `/admin/exports` page loads on the deployed staging service. This verifies that page only; it is not a full authenticated browser acceptance run against every workflow.
- **Render:** `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) is live on the `secondary-school-platform-foundation` branch, Free plan, Frankfurt region, with auto-deploy disabled. Latest deployment `dep-dbo2l1h5efls73cnf8j0` completed successfully. The Render event feed shows successful build/deploy events and no failure events in the returned window. Error-log query returned no rows. HTTP request/latency and CPU metrics returned no data; memory returned one sample (~85 MB). Render notification setting is `default`; no test alert or delivery evidence is available.
- **Neon staging:** project `learnwise` is in `aws-eu-central-1`; branch `think-tank-staging` is ready. Read-only counts: 0 students, 6 subjects, 0 topics, 1 active admin, 20 migration-history rows. Latest migration is `020_private_student_export_approval`, applied 2026-11-08T07:53:34Z; recorded source blob SHA `3ee86c0d909f429f6ca5787c47b51f86dfdf9a13`.
- **Private storage:** existing `learnwise-private-audio` is private and empty. Created a separate private staging bucket `think-tank-private-exports` at 2026-11-08T08:04:40Z and verified both buckets are private. No export credentials have been configured; the available Neon scoped-storage credential would grant branch-wide storage access rather than bucket-only access, so it was not issued. The worker remains disabled and unscheduled.
- **Audio provider acceptance:** a synthetic WAV was prepared and a short-lived upload URL was issued, but the execution host could not resolve the Neon storage hostname. No object was uploaded; real upload/playback/range/revocation remains unverified.
- **SMTP/password recovery:** Brevo variables were previously owner-reported as configured, but the connected Render tools cannot safely read variable presence and no live application delivery/reset confirmation is recorded. Mocked transport tests are not provider delivery evidence.
- **Paystack:** no sandbox transaction/webhook/refund evidence is recorded; sandbox credentials and controlled test account remain required. Live payments remain disabled.
- **NERDC:** source register records official acquisition routes, but full source capture/licensing and teacher sign-off for all 18 class/subject combinations are incomplete. Staging has zero topics; do not publish unlicensed or unreviewed content.
- **Safeguarding/privacy/legal:** guardian consent evidence, safeguarding lead approval, NDPA/DPIA and retention approval, and qualified Nigerian legal review remain outstanding.
- **Backup/recovery:** Neon snapshot list and staging-branch snapshot schedule are empty. The existing backup branch is ready, but its endpoint is unavailable for a read/restore test. The attempted snapshot operation was rejected because the staging branch is a non-root branch. Managed PITR/restore, measured RPO/RTO and recovery-owner sign-off remain outstanding. CI's disposable local backup/restore test is not a managed restore drill.
- **Independent security review:** not performed by an independent reviewer. Automated tests and internal code checks do not substitute for it.
- **Export approval:** only one active administrator exists, so two-person approval cannot yet be exercised. The private bucket is provisioned but credentials, a second authorised administrator, a controlled export test and worker scheduling are outstanding. No export job has run.
- **Safety:** no production deployment, PR merge, main-branch change, live payment, owner-admin bootstrap, or student-data processing was performed in this audit. PR #1 remains open/draft/unmerged.

### Owner actions required to clear external gates
1. Verify the Brevo sender and run registration/verification plus password-reset delivery to an owner-controlled mailbox; keep registration closed except during a controlled test.
2. Add Paystack sandbox credentials directly in the staging secret manager and authorise a controlled sandbox checkout/webhook/refund test. Never paste keys into chat.
3. Decide whether export storage will use a separate S3-compatible provider with bucket-scoped credentials or accept Neon branch-wide storage credentials after a security review. Do not enable the worker before this decision and a second authorised administrator exist.
4. Obtain written NERDC access/reuse terms and provide the authorised source material through an approved channel; appoint qualified subject teachers for the 18 mappings.
5. Appoint Nigerian privacy/legal counsel and a safeguarding lead; obtain guardian-consent, NDPA/DPIA, retention and incident-response approvals.
6. Confirm an approved backup/PITR plan and recovery owner; restore to an isolated branch and record measured RPO/RTO.
7. Name an alert recipient/on-call owner and run a controlled notification test; arrange an independent security assessment.

Production/student onboarding remains blocked until all applicable release gates have documentary evidence and separate owner approval.


### Latest staging execution update — 8 November 2026
- **Render:** latest deployment `dep-dbo9jk0u01pc73ekc330` is **live** on commit `36141466a8226a6f5e4d91b1d6a08f1ebe1d2c79`. Private-audio key and byte-range validation hardening is deployed. Auto-deploy remains disabled.
- **CI and health:** workflow run [42478184387](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42478184387) passed all three jobs. Its post-deployment staging health job recorded HTTP 200 and JSON `status=ok`, `mode=database`, `service=secondary-school-api`. API tests included PostgreSQL integration and disposable-fixture browser acceptance; they did not test real learner accounts or external provider delivery.
- **SMTP:** owner-only staging diagnostic is enabled, but the recorded attempt returned `smtp_diagnostic_unavailable`; Brevo delivery remains failed/unverified. The diagnostic now logs only bounded failure phase and exception class. Do not retry until logs and rate-limit window are checked.
- **Private storage:** owner reports R2 credentials configured directly in Render; their presence has not been independently inspected. No object PUT/GET/checksum, unsigned denial, cross-bucket isolation or deletion acceptance has been run. Keep export worker disabled. Audio hardening deployment does not prove live audio upload/playback acceptance.
- **Other gates remain open:** Paystack sandbox E2E; live-staging authenticated browser acceptance; safe synthetic student invitation and verification/reset lifecycle; curriculum rights and qualified teacher review; safeguarding/guardian consent/NDPA/DPIA; Nigerian legal review; managed backup restoration; monitoring alert delivery; second administrator; independent security review.
- **Release restrictions:** public student registration, exports, live payments, production launch and PR merge remain disabled/not authorised. `main` remains untouched. See `DEPENDENCY_EXECUTION_CHECKPOINT_2026-11-08.md` for detailed evidence and blockers.


### Live staging browser acceptance — 8 November 2026
- **Passed:** read-only Playwright browser run [42497224093](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497224093), 9/9 tests against live staging. Verified public readiness, student page delivery, account form presence, keyboard/mobile accessibility, anonymous denial of student/private learning/assessment/audio APIs, and anonymous admin protection/redirects.
- **Not passed / still outstanding:** authenticated live-staging browser acceptance. The live workflow deliberately excludes authenticated write tests because they create assessment/export/privacy-request records and there is no approved synthetic student test account. No live account or learner data was touched.
- The read-only workflow now runs automatically when its workflow file changes on the development branch; its manual-dispatch option remains. No application deployment was triggered; Render auto-deploy is disabled.


### Fresh Neon audit — 8 November 2026
- Staging read-only counts: 0 students, 1 active administrator, 0 topics, 0 approved curriculum source records, 20 migration-history rows.
- Snapshot listing is empty; automatic snapshot schedule for the staging branch is empty. Existing copied backup branch is not a managed snapshot or a verified restore. Managed recovery remains outstanding.
- No database data or backup settings were changed.
- The identity review confirms a QA provisioning design must keep synthetic records distinct and must never represent terms/privacy acceptance as guardian consent. Public registration remains disabled; no synthetic account was created.


### Private audio data-plane test attempt — 8 November 2026
- Neon confirms the staging audio bucket exists and is private. A synthetic 76-byte test payload and short-lived presigned upload were prepared.
- Upload could not be attempted successfully because the execution host could not resolve the Neon storage hostname (HTTP 000 / DNS failure). A subsequent bucket-prefix listing confirmed no test object was created.
- This is a transport-blocked attempt, not a passed storage test. Real upload, retrieval/checksum, access denial, playback/range and deletion remain outstanding pending a runtime/network that can resolve the storage endpoint.


### Synthetic QA lifecycle design checkpoint — 8 November 2026
- Added `STAGING_SYNTHETIC_QA_IDENTITY_SPEC.md` on the development branch. It defines staging-only owner-authorised provisioning, configured-recipient-only invitation, hashed single-use verification, immutable synthetic identity marking, default-deny learner-data access, expiry/revocation, audit logging and cleanup.
- This was the initial design checkpoint. The schema, service, owner-only routes, synthetic-session isolation and tests were subsequently implemented and deployed to staging; no live synthetic account has been created. Existing student registration must not be reused because it writes privacy/terms acceptance records; no guardian-consent record may be fabricated.
- PR workflow run [42497551018](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497551018) completed successfully: API tests, PostgreSQL migration/integration and disposable authenticated browser suite, staging health, and container build all passed. This is CI against disposable fixtures, not authenticated acceptance against live Render.
- Public student registration remains disabled; no staging application deployment, PR merge or main-branch change was made.



### Synthetic QA lifecycle implementation and staging migration — 8 November 2026
- Implemented the staging-only synthetic QA lifecycle on the development branch: migration 021; owner-session + CSRF + `settings.manage` provisioning/revoke/expiry endpoints; fixed configured mailbox; hashed one-time verification token; temporary password delivered only by email; 24-hour identity expiry; synthetic-session default-deny; and revoke/expiry invalidation.
- Synthetic identities are excluded from admin learner counts/lists, payment/finance views, Paystack checkout, assessment creation, profile services, self-service exports, and approved bulk exports. QA provisioning writes no privacy/terms acceptance or guardian-consent records.
- Added unit route tests, export-isolation tests, and disposable-PostgreSQL lifecycle tests covering token hashing, verification, login, no consent rows, expiry, session revocation, mailbox clearing and feature-flag fail-closed behavior.
- Full push CI [42499289104](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42499289104) and PR CI [42499293173](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42499293173) passed all three jobs, including PostgreSQL synthetic QA lifecycle, migration replay, backup/restore rehearsal, schema integration, assessment/payment E2E, student journey, disposable authenticated browser acceptance, staging health and container build.
- Migration 021 (`021_synthetic_qa_identity.sql`, source blob SHA `f7a08dc396534ee7bb8be25d656bf49415ba862e`) was rehearsed and recorded on Neon branch `think-tank-migration-rehearsal-2026-11-08` and then applied transactionally to staging branch `think-tank-staging`. Both now report 21 migration-history rows; staging has 0 students, 0 synthetic students, 1 active administrator and 0 consent rows.
- No synthetic account was created. The feature remains disabled unless `APP_ENV=staging`, `STAGING_QA_IDENTITY_ENABLED=true`, `STUDENT_REGISTRATION_ENABLED=false`, and a configured `STAGING_QA_EMAIL` are all satisfied. SMTP delivery must work before provisioning can succeed.

### R2 private-object acceptance — 8 November 2026
- Cloudflare R2 control-plane object test passed against `think-tank-private-exports`: uploaded an 86-byte synthetic text object, retrieved exact matching bytes, verified SHA-256 `5ff962c3b80980c5ae718d0e10fa3e890119d9278b928989ef8dab364625ebb0`, confirmed listing metadata, deleted the object and confirmed the QA prefix was empty.
- Bucket's managed `r2.dev` public domain is disabled and no custom domains are attached. This supports the private-access configuration check.
- A direct anonymous GET could not be completed because the execution host could not resolve the `r2.dev` hostname. Therefore a request-level unsigned 403/404 is not claimed. This Cloudflare control-plane test also does not yet prove the Render application's configured S3 credentials work.

### Neon private audio retry — 8 November 2026
- Confirmed branchable storage enabled and `learnwise-private-audio` remains private on `think-tank-staging`. A fresh short-lived presigned PUT was attempted from the execution host; DNS resolution of the Neon storage hostname again failed. The `qa-acceptance/` prefix remains empty. No audio object was uploaded; playback, checksum, range, denial and deletion remain blocked.

### Render staging deployment — 8 November 2026
- Manually triggered staging deployment `dep-dboa3995efls73d9hd70` for exact CI-tested commit `c691d6026588ab36d2c5cd7de73fd9567a792b00`. Render build completed successfully; deployment rollout was still in progress at the time of this checkpoint. Auto-deploy remains disabled.
- No production deployment, PR merge, main-branch change, live student registration or live payment was performed.



### Post-deployment live acceptance — 8 November 2026
- Render deployment `dep-dboa3995efls73d9hd70` completed with status `live` at 2026-11-08T16:23:40Z on exact commit `c691d6026588ab36d2c5cd7de73fd9567a792b00`. Build succeeded; service remains Free and auto-deploy remains disabled.
- After rollout completion, live read-only browser workflow [42499695470](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42499695470) passed **9/9** against the deployed staging service: health readiness, student page delivery, account controls, keyboard/mobile accessibility, anonymous student/private API denial, anonymous assessment/audio denial, anonymous admin denial and admin redirect/login separation. No real form submission or learner data write occurred.
- The same browser run's health test passed after deployment. Earlier health job run 42499619472 occurred while rollout was still finishing and is not used as post-deploy evidence.
- Authenticated live student acceptance remains outstanding. The synthetic QA flow is implemented and its disposable PostgreSQL + browser tests pass, but no staging QA identity was provisioned because SMTP/Brevo delivery has not been verified and the dedicated QA mailbox/feature flag are not enabled.
- R2 control-plane object upload/retrieval/checksum/delete acceptance passed as recorded above; direct anonymous URL request remained DNS-blocked. Render application's S3 credentials remain untested.
- Neon private audio upload/playback remains transport-blocked by execution-host DNS; no QA object exists in the private audio bucket.



### R2 anonymous-denial verification completed — 8 November 2026
- A second synthetic 86-byte object was uploaded to the private R2 bucket solely for a public-access check. The GitHub Actions runner made an unauthenticated GET to the exact managed `r2.dev` object URL and received **HTTP 401**, confirming denial of anonymous retrieval.
- Read-only browser workflow [42499890634](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42499890634) passed the R2 anonymous-denial step and all 9 live staging browser tests.
- The temporary object was deleted through the Cloudflare API. A final list of the `qa-acceptance/` prefix returned zero objects.
- The earlier local-container DNS failure is superseded for the R2 public-access check by this successful GitHub-runner HTTP 401. Neon private-audio DNS remains unresolved.

## Post-deployment acceptance update — 8 November 2026, 16:37 UTC

- Fresh post-deploy staging-health workflow on branch commit `51e4efb152c762f9e350e4446d19dd86da8db0c5` passed after Render deploy `dep-dboa96nig07c73a2dlf0` became live. The public `/health` probe returned the expected healthy database-mode service response.
- Fresh read-only live staging Playwright run `42500709060` passed **9/9** tests after the new deployment. Verified health, student-facing page delivery, account controls without submitting real data, mobile/keyboard accessibility, anonymous learner/assessment/audio denial, anonymous admin denial, admin redirect and separate admin login page.
- The authenticated browser suite passed on disposable PostgreSQL fixtures in CI; authenticated live staging remains blocked because no synthetic QA identity has been issued. No student rows exist: Neon staging counts show total students 0, synthetic QA students 0, real students 0; active admins 1; approved curriculum sources 0; topics 0.
- A second direct presigned Neon Storage upload attempt was made from the available execution network using a fresh five-minute URL and synthetic text payload. DNS resolution again failed before connection (HTTP 000, curl exit 6); the object was not uploaded and the bucket listing remains clean. This confirms an execution-network limitation, not a Neon storage outage. Repeat from Render runtime is still required.


## Staging diagnostics enablement — 8 November 2026, 16:47 UTC

- Added an owner-only, CSRF-protected, settings.manage-gated private storage acceptance endpoint and button on /admin/operations. It runs from the Render application runtime, not the model-side network, and uses only synthetic WAV payloads. For both private audio and R2 export buckets it performs PUT, GET, SHA-256 comparison, unsigned GET denial and DELETE/absence verification. It records only safe result metadata and hashes; no secrets or learner data are returned. One attempt per admin per 15 minutes. Cross-bucket denial is not covered because no second bucket-scoped R2 test credential/known alternate bucket is configured.
- Enabled STAGING_STORAGE_DIAGNOSTICS_ENABLED=true on staging. The owner can now sign in at /admin/operations and click “Run private storage acceptance”. No diagnostic has yet been run; storage acceptance remains outstanding until the button is used.
- Added an owner-only synthetic QA invitation/revoke/expiry panel on the same page. Enabled STAGING_QA_IDENTITY_ENABLED=true and configured the QA recipient to the previously confirmed owner mailbox. Public student registration remains disabled. No synthetic identity has been issued. The owner must click “Send synthetic QA invitation”, verify the email link and sign in with the temporary password; if SMTP submission fails, the pending account is revoked automatically.
- New Render deployment dep-dboaenuc6qcc73d3lc00 is live on commit a9b7bacd4c3069651319df79ce95ec932a7797fc after the environment update. Render application logs showed no error/exception/traceback entries in the post-deploy sample.
- Push CI 42501474162 and PR CI 42501478189 passed all jobs on the application commit, including new storage diagnostic unit/route tests, PostgreSQL migration and restore rehearsals, synthetic identity lifecycle tests, authenticated/anonymous local browser tests, container build and staging health. Read-only live browser run 42501474212 passed 9/9 before the environment-flag deploy; a fresh post-environment-update health/browser run is triggered by this checkpoint update.


## Latest verified staging state — 8 November 2026, 16:51 UTC

- Current development branch head: d66cca79bb12221de7228ffc8b49e4b5167f6f66. PR #1 remains draft/open/unmerged; main remains untouched.
- Application deployment: Render deployment dep-dboaenuc6qcc73d3lc00 is live on application commit a9b7bacd4c3069651319df79ce95ec932a7797fc. Render auto-deploy remains disabled.
- Staging feature flags: owner-only storage diagnostics and synthetic QA invitation are enabled. Public student registration remains disabled. Export worker and live payments remain disabled.
- Exact-head push CI 42501847900 and PR CI 42501852204 both passed all jobs: unit/security, syntax, disposable migration replay, local backup/restore, PostgreSQL schema and lifecycle tests, assessment/payment E2E, student journey, authenticated/anonymous local Playwright and non-publishing container build. Staging health passed.
- Fresh read-only live browser run 42501847936 passed 10/10 tests against staging after the environment update. It confirmed healthy service, student pages, registration UI, keyboard/mobile accessibility, anonymous learner/assessment/audio denial, owner-only QA/storage diagnostics (401 without admin session), anonymous admin denial, admin redirects and separate login. The test also confirms public registration remains closed.
- Neon staging: migration 021 is applied; counts remain 0 students, 0 synthetic QA students, 1 active admin, 0 approved curriculum sources and 0 topics.
- Cloudflare account inventory contains exactly one R2 bucket, think-tank-private-exports. Its managed r2.dev domain is disabled. Neon reports both learnwise-private-audio and think-tank-private-exports as private buckets. No second R2 bucket was created; cross-bucket denial therefore remains untested.
- The owner-only storage diagnostic control is live at /admin/operations. It has not been run yet. Owner must click “Run private storage acceptance” to execute synthetic audio/R2 PUT, GET, SHA-256, unsigned-denial and DELETE/absence checks from the Render runtime.
- The synthetic QA invitation control is live on the same page and targets the configured owner mailbox. No synthetic account has been issued. Owner must click “Send synthetic QA invitation”, verify the emailed link and sign in. SMTP delivery is not yet verified; a failed send automatically revokes the pending identity.
- Authenticated live-staging acceptance remains outstanding until the owner completes the invitation/verification and tests the signed-in synthetic account. CI authenticated tests use disposable local fixtures only.




### Staging diagnostics ready for owner execution — 8 November 2026, 16:55 UTC
- Explicit staging environment settings are now in place: `APP_ENV=staging`, `STUDENT_REGISTRATION_ENABLED=false`, `STAGING_STORAGE_DIAGNOSTICS_ENABLED=true`, `STAGING_QA_IDENTITY_ENABLED=true`; the synthetic QA recipient is the confirmed owner mailbox. No student account was created by configuration.
- Render deployment `dep-dboaidjrjlhs73asffug` is **live** on commit `d803ece32de57bbffd3ede3ad48b52e951ab7e64`. Service remains Free; Render auto-deploy remains disabled.
- The live read-only browser suite [42501984433](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42501984433) passed after the environment flags were enabled. It verifies the synthetic QA and storage diagnostic endpoints reject anonymous callers with HTTP 401, alongside the existing public-page, accessibility and anonymous-denial checks.
- Push and PR CI [42502089029](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42502089029) and [42502095096](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42502095096) passed all jobs: unit/security, migration replay, local backup/restore rehearsal, PostgreSQL schema and lifecycle tests, assessment/payment tests, disposable authenticated browser acceptance, staging health and container build.
- Neon staging independently rechecked: migration history 21 rows (latest 021), 0 students, 0 synthetic students, 1 active owner administrator, 0 consent rows. Both `qa-acceptance/` prefixes remain empty in Neon audio and export buckets.
- The owner-only controls are ready at `/admin/operations`: send the synthetic QA invitation, run private storage acceptance, or retry the SMTP diagnostic. **Neither the storage diagnostic nor synthetic QA invitation has been executed yet.** The storage probe runs from the Render runtime and is the next required technical acceptance. SMTP/Brevo delivery remains unverified; a failed invitation automatically revokes the pending synthetic identity.
- Authenticated live browser acceptance remains outstanding until the owner receives and verifies the QA invitation. The synthetic account is isolated and cannot access learner records, assessments, payments, exports or private learning content.


## Final branch/reference check — 8 November 2026, 16:55 UTC

- Development branch latest commit before this note: d77ab84e0c1e044795f26b8311160496edb1da63. PR #1 remains draft/open/unmerged.
- Main is restored to 5d6d93ceec31ff3eb6851d567e4d61f7477bc492, its pre-checkpoint head; the temporary documentation-only commits were rolled back. No lasting main-branch changes remain.
- Application remains deployed to staging only at dep-dboaenuc6qcc73d3lc00 / a9b7bacd4c3069651319df79ce95ec932a7797fc.
- Exact-head push/PR CI and live browser evidence at d803ece32de57bbffd3ede3ad48b52e951ab7e64 are green; current documentation-only head d77ab84e0c1e044795f26b8311160496edb1da63 has fresh CI/browser checks running.
- Owner actions still required at /admin/operations: run private storage acceptance, then send and verify the synthetic QA invitation. No synthetic account or storage test object has been created. Public student registration remains disabled.



## Final verification — 8 November 2026, 16:58 UTC

- Development branch before this note: 01ee3dfbbb9445c5207b190b7ad9a77c56b76e4e. Latest exact-head push CI 42502439706 and PR CI 42502443706 both passed all three jobs.
- Live read-only staging browser run 42502439746 passed 10/10, including owner-gated QA/storage endpoints returning 401 to anonymous callers and the disabled public-registration response.
- Application deployment remains dep-dboaenuc6qcc73d3lc00 on a9b7bacd4c3069651319df79ce95ec932a7797fc. The newer commits are documentation/test-only; no further app deploy was needed.
- Main remains at its original pre-checkpoint head 5d6d93ceec31ff3eb6851d567e4d61f7477bc492. PR #1 remains open/draft/unmerged.
- Owner-only controls are ready at /admin/operations. Storage probe and synthetic QA invitation have not been executed; no synthetic identity or storage test object exists. The owner session is required to run them.



## Storage acceptance enablement and post-deploy verification — 8 November 2026, 17:10 UTC

- Render staging flag `STAGING_STORAGE_DIAGNOSTICS_ENABLED=true` is enabled. Deployment `dep-dboapnh5efls73dbg5ug` completed successfully on code commit `771f5afa225a67503dd3d5d786a7cd7eb89c61ee`.
- The Operations page has an owner-only **Run private storage acceptance** control. The route is staging-only, requires owner session + CSRF + `settings.manage`, rate-limits to one run per 15 minutes, and tests only random synthetic objects. It verifies upload, retrieval, SHA-256, unsigned-access denial and deletion/absence for private audio and R2 export buckets. It records an audit event and never uses learner data.
- Enabling the flag only exposes the protected diagnostic; it does not execute it. No owner-triggered run has been recorded. R2 and audio object-level acceptance therefore remain **pending**, not passed. The signed-in owner must click the control at `/admin/operations` and preserve the returned result. Do not bypass authentication or use production.
- Synthetic QA identity flag remains disabled; no test account has been created. Public registration, live payments and export worker remain disabled.
- Previous CI/browser results predate this deployment. This documentation push triggers fresh read-only staging health and browser checks against the deployed service. These do not constitute authenticated live-staging acceptance.

No storage object test, live audio playback, Paystack sandbox transaction, production deploy, PR merge or main-branch change was performed in this step.


## Final verification after storage-diagnostic enablement — 8 November 2026, 17:12 UTC

- Render deployment `dep-dboapnh5efls73dbg5ug` is live on `771f5afa225a67503dd3d5d786a7cd7eb89c61ee`; the only environment change was enabling the staging-only owner storage diagnostic flag.
- Post-deployment health check on the subsequent branch push returned HTTP 200 and JSON `status=ok`, `mode=database`, `service=secondary-school-api` (workflow `42503698390`, staging-health job).
- Post-deployment live read-only browser acceptance `42503693149` passed **10/10**. In addition to the nine baseline checks, it verified the synthetic QA and storage diagnostic endpoints reject anonymous callers. This was after the deployment and flag enablement; it did not use an authenticated owner session or create test data.
- Exact-head push CI `42503693130` passed all three jobs on commit `54868ed2b6ef42ebde4485877407399978113b55`: API/security tests, PostgreSQL migration and restore rehearsal, schema/lifecycle/assessment/payment/student-journey tests, authenticated+anonymous browser tests on disposable fixtures, container build, and staging health.
- The owner-only storage diagnostic is available at `https://learnwise-staging-api.onrender.com/admin/operations`. Its actual R2/audio object probes remain unexecuted until the owner signs in and clicks **Run private storage acceptance**. Do not report storage as passed before the returned results confirm all five checks for each bucket.
- Synthetic QA feature remains disabled. The next authenticated live-staging test requires a dedicated mailbox and verified SMTP delivery, then an owner-triggered synthetic invitation. No learner account or consent has been fabricated.

All other human/provider/recovery release gates remain open: Paystack sandbox; approved/licensed curriculum and teacher sign-off; safeguarding/guardian consent/NDPA/DPIA; Nigerian legal review; managed backup restore; monitoring alert delivery; second administrator; independent security review.


## Configuration correction — synthetic QA gate state — 8 November 2026, 17:14 UTC

The latest post-deployment live browser run `42503828381` returned HTTP 401 from the synthetic QA issuance endpoint to an anonymous caller. The route returns 404 before authentication when its staging feature gate is disabled. Therefore `STAGING_QA_IDENTITY_ENABLED` is **enabled** on staging, and the independent `STUDENT_REGISTRATION_ENABLED=false` guard is also in effect. The prior 17:10 addendum incorrectly said the synthetic QA feature flag remained disabled; this correction supersedes that sentence.

This does **not** mean an identity was created or invitation delivery verified. Neon staging still has 0 students and 0 synthetic QA identities. No invitation was sent by this run. The configured QA recipient value cannot be inspected through the available read-only Render service metadata, and SMTP/Brevo delivery remains unverified. The owner-only invitation control is available on `/admin/operations`; it must be used only with a dedicated QA mailbox and verified delivery. If invitation delivery fails, the route revokes the pending synthetic identity. Do not treat HTTP 401 as proof of authenticated access or email delivery.


## Final staging safety configuration — 8 November 2026, 17:25 UTC

- Render deployment `dep-dbob0qh5efls73dc3tg0` completed successfully (Render deploy-ended event `evt-dbob11rm5ojs73fvl1hg`). The deployment picked up the explicit staging environment change `STAGING_QA_IDENTITY_ENABLED=false`.
- Reason: anonymous browser verification had shown HTTP 401 on the QA issuance route, proving the route was exposed behind authentication, but no dedicated QA mailbox or verified Brevo delivery was available. The safe decision is to keep QA issuance disabled until mail delivery and recipient ownership are verified. This prevents an owner from accidentally issuing an invitation to an unverified address.
- The independent owner-only storage diagnostic remains exposed by `STAGING_STORAGE_DIAGNOSTICS_ENABLED=true`. Its data-plane test is still not run; it must be triggered by the authenticated owner in the staging Operations page.
- No student account was created. Student public registration remains disabled. The staging deployment has not been re-tested after the 17:25 environment update yet; trigger/record a fresh health and read-only browser check before claiming post-update health.

No secrets were read or changed, no data was created, and no production/PR/main action occurred.


## Verification closure after fail-closed QA gate correction — 8 November 2026, 17:29 UTC

- Render staging deployment `dep-dbob0qh5efls73dc3tg0` is live and succeeded after setting `STAGING_QA_IDENTITY_ENABLED=false`. The independent storage diagnostic flag remains enabled for the authenticated owner-only operations control.
- The first read-only browser rerun correctly exposed an overly strict test expectation: a disabled QA feature returns HTTP 404, not HTTP 401. The app behavior was safe; the test was corrected to accept either 401 (enabled but owner-authenticated) or 404 (feature disabled), for both QA and storage diagnostics. No application security gate was weakened.
- Final exact-head commit: `69ac72efe2bd07fe4419821cf80b315196ba55bf`.
- Push workflow `42505118443`: all three jobs passed (API/security + PostgreSQL migration/lifecycle/student journey/authenticated disposable browser suite; container build; live staging health).
- PR workflow `42505121608`: passed on the same exact head.
- Live staging read-only browser workflow `42505118340`: **10/10 passed** after the staging safety deployment. It confirmed student pages, registration controls without submitting data, mobile/keyboard access, anonymous identity/private learning/assessment/audio denial, QA/storage diagnostic fail-closed responses, admin identity denial and admin login separation.
- This is still anonymous/read-only live acceptance, not authenticated live QA. No synthetic account exists; QA issuance stays disabled pending a dedicated mailbox and verified SMTP delivery.
- Storage data-plane acceptance is still outstanding. The owner-only control is available at `/admin/operations`; an authenticated owner must run it to test synthetic object PUT/GET/checksum/unsigned denial/delete for private audio and R2. No storage pass is claimed.

The staging-health CI check passed after the 17:25 environment deployment. Public registration, export worker and live payments remain disabled. No production deployment, PR merge, main-branch change, paid upgrade or real student data operation occurred.


### Follow-on provider diagnostic investigation — 8 November 2026

- Latest documentation/handover branch head is now `abf294789c46b6a06aff5e6e7e19f17e22a50b8a`; application runtime files are unchanged from the currently deployed Render commit.
- Render logs show three failed SMTP diagnostic attempts and no successful delivery evidence. The code requires `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, optional port 587/465, valid `SMTP_FROM`, and HTTPS `PUBLIC_APP_URL` for identity links. No secret values were inspected or changed.
- The storage acceptance code is confirmed to test private audio and R2 synthetic WAV PUT/GET/SHA-256/unsigned denial/DELETE. No storage-probe logs were found; no object test is recorded as passed.
- Both owner-only controls require the authenticated admin browser session and CSRF. The connected infrastructure tools cannot access that session or execute an in-container command; neither diagnostic was invoked from this run. No synthetic QA invitation/account was created.
- **Still blocked:** actual SMTP delivery/account recovery; private storage object acceptance; owner-issued and verified synthetic QA identity plus authenticated live browser acceptance; Paystack sandbox; licensed curriculum/teacher review; safeguarding/guardian consent/NDPA/DPIA/Nigerian legal sign-off; managed restore/RPO/RTO; monitoring alert delivery; second administrator; independent security review.
- No secrets, environment variables, application deployment, migration, database records, storage objects, payment, PR state or main-branch state were changed during this follow-on.
