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
- Added `migrations/004_student_profiles_and_assessments.sql` with learner profile metadata, explicit consent records, assessment definitions/questions/attempts/answers, and notification records.
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
- Default timing is 36 seconds per selected question: 5 = 3 minutes, 10 = 6 minutes, 50 = 30 minutes, 100 = 60 minutes. The earlier 10 = 7 example conflicts with the other examples and is documented as a mismatch, not silently encoded.
- Each attempt requires a mandatory pre-test briefing and per-attempt affirmative agreement.
- Three qualifying focus/visibility/fullscreen incidents: warnings on incidents one and two; third incident ends the attempt and submits server-persisted answers.
- Browser restrictions are deterrents, not guarantees: a website cannot prevent screenshots, second devices, external cameras, or every OS/browser route. Integrity signals can false-positive; termination is flagged for review and appeal, not treated as conclusive cheating.
- Server-authoritative timer, answer persistence, immutable assessment versions, idempotent terminal states, objective grading, accessibility and minor-safety acceptance tests are specified.
- These rules are requirements only. They are NOT yet implemented in a live student test service.

## Latest implementation caveat
The student and admin profile/assessment additions require a fresh GitHub Actions run to pass before the expanded test suite is considered verified.
