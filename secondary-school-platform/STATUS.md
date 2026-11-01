# Implementation status

Last updated: 2026-11-01

## Verified project state
- Work is isolated in `secondary-school-platform/` on `secondary-school-platform-foundation`.
- Draft pull request #1 remains open and unmerged: https://github.com/JephterAce/Year-1-Tutorial/pull/1
- Product scope: SS1–SS3 and six subjects — English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics.
- Student portal prototype at `frontend/index.html`; dashboard now displays six subjects. Sample topics are illustrative only and are not assigned to verified class-specific sequences or terms.
- Catalogue term filter now reflects the actual data state: term allocation pending verification. It does not imply verified First/Second/Third Term placement.
- Admin workspace at `admin/index.html` remains a static design preview.
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
- Latest student UI correction committed: subject count 5 → 6; term filter now matches pending term-allocation metadata; catalogue notice clarifies that sample topics are not class/term-verified.

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
- Later commits were not covered by those historical runs. A fresh run must be verified against the latest branch head before claiming the current state passes CI.

## Safety and release status
The student and admin interfaces remain prototypes. The API does not yet handle production accounts, payments, real student data or protected audio. No production database has been connected, no migrations have been applied, and no live service or legacy university bot has been changed or deployed.

Keep PR #1 in draft. Do not merge, deploy, spend money, or modify the legacy university bot without the owner's explicit approval.
