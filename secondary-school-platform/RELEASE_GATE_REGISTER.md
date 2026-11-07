# Learnwise release gate register

**Status date:** 2026-11-02  
**Branch:** `secondary-school-platform-foundation`  
**Release posture:** NOT APPROVED FOR PRODUCTION OR PUBLIC STUDENT USE

This register separates repository work that can be tested in CI from approvals, provider access and operational actions that require the owner or an independent authority. A green CI run is not a substitute for those approvals.

## Verified engineering evidence

The latest recorded GitHub Actions run on the branch head must be checked before each release decision. At the 2026-11-02 checkpoint, commit `9049c00a3f40eeb7348953b1ac59c155040ca711` had a successful run with these completed jobs/steps:

- Python unit and security tests.
- Frontend and admin JavaScript syntax checks.
- Disposable PostgreSQL 16 baseline + numbered migration replay.
- PostgreSQL schema integration tests, including replay idempotency and append-only audit event checks.
- Database-backed assessment attempt/start/answer/submit flow.
- Mocked Paystack checkout, webhook signature, server-side transaction verification and idempotent entitlement fulfilment.
- Container image build without publishing.

These tests use disposable CI infrastructure and fake Paystack responses. They do not prove operation against a live provider account, a real storage service, a deployed environment or real student devices.

## Release gates

| Workstream | Repository preparation | External evidence required | Release status |
|---|---|---|---|
| PostgreSQL and CI | Migration runner, disposable PostgreSQL CI, schema and end-to-end tests | Owner-approved managed DB, access controls, backup/restore rehearsal, production migration plan | CI verified; production DB not connected |
| Student/admin interfaces | Student catalogue, account/profile, lesson and assessment pages; admin prototype/auth foundations | Full browser/device acceptance, accessibility review, role-by-role admin tests, real DB-backed UAT | Partial; UAT outstanding |
| Assessments | Server-authoritative timing, snapshots, grading, attempts, reports and database integration tests | Teacher assessment review, browser/mobile/network recovery tests, admin adjudication UAT | CI flow verified; operational acceptance outstanding |
| Payments | Server-priced Paystack checkout and mocked webhook/verification/idempotency tests | Owner supplies Paystack test credentials through secret manager; real sandbox transaction, webhook delivery/retry, reconciliation and refund tests | Mocked CI only; sandbox account test outstanding |
| Private audio | Short-lived signed access tokens, entitlement checks and private local-root path confinement | Approved private object-storage provider/bucket, credentials in secret manager, upload/stream/range tests and access-log review | Local private-storage foundation; provider adapter/UAT outstanding |
| Privacy and safeguarding | Private-by-default profile, consent capture, access boundaries, audit and export serialization foundations | Nigerian counsel/privacy professional review, safeguarding lead approval, guardian/child consent and retention decisions, incident-response sign-off | Not approved |
| Hosting and operations | Non-root container, health endpoint, deployment/operations documentation | Hosting account and credentials, real staging environment, TLS/DNS, secrets, monitoring/alerts, backup/restore proof and owner deployment approval | Prepared only; no staging deployed |
| NERDC curriculum | Versioned source register, import template, provenance/rights metadata, evidence-gated publication workflow | Authorised NERDC materials/access and licence; independent teacher verification; cohort/term applicability evidence | No authorised curriculum corpus imported; not verified |

## Owner-provided prerequisites

Do not put credentials in Git, issue comments, email drafts or ChatGPT messages. Configure them directly in the selected provider's secret manager after access is granted.

1. **NERDC access:** identify the authorised institutional/account route and provide licensed source files or access through an approved secure workflow. Include the applicable curriculum edition, subject scope, SS1–SS3 cohort transition evidence and any term allocation/scheme-of-work materials. Do not share passwords in chat.
2. **Teacher verification:** appoint an independent qualified Nigerian secondary-school teacher per subject (and a second reviewer for disputed/high-impact material). Each reviewer must sign off topic accuracy, class level, learning outcomes, sequencing and assessment alignment.
3. **Legal and safeguarding approval:** appoint Nigerian privacy/legal counsel and a safeguarding lead. Approve privacy notice, lawful basis, child/guardian consent, age-appropriate design, retention/deletion, data-subject requests, breach handling, payment disclosures, complaints and incident escalation.
4. **Paystack sandbox:** create/identify the Learnwise Paystack test account and configure test secret/public keys and webhook secret directly in a secure secret manager. No live key is needed for sandbox testing.
5. **Hosting/staging:** select the hosting provider and managed PostgreSQL/object-storage services; grant least-privilege project access; configure a staging domain and TLS. Provide a written staging deployment approval before any deployment action.
6. **Operational owner:** name the person responsible for on-call alerts, payment reconciliation, backups, restore exercises, security incidents and student-support escalation.

## Staging release checklist

- [ ] All CI checks pass on the exact release commit.
- [ ] Disposable migration replay and backup/restore rehearsal pass.
- [ ] Staging database is isolated from production and contains synthetic data only.
- [ ] All secrets are set in provider secret manager; no secrets in repository or build logs.
- [ ] HTTPS, secure cookies, CSRF/origin controls, rate limits and security headers are verified.
- [ ] Private audio objects are not served from a public/static bucket; entitlement revocation blocks subsequent playback.
- [ ] Paystack sandbox charge, signature validation, server-side verification, duplicate webhook, delayed webhook, failure and refund/reversal scenarios pass.
- [ ] Student and admin journeys pass browser, mobile, accessibility and role-permission tests.
- [ ] Monitoring, actionable alerts, structured logs, audit retention and error reporting are verified without exposing student secrets.
- [ ] Automated backup and a timed restore exercise pass; RPO/RTO are documented.
- [ ] Privacy, legal and safeguarding sign-offs are recorded.
- [ ] NERDC source rights, teacher verification and curriculum cohort mapping are recorded for every published lesson.
- [ ] Owner explicitly approves staging deployment.

## Safety boundaries

- Do not deploy, run production migrations, activate live payments, purchase services or alter live secrets without explicit owner approval.
- Do not import guessed or unauthorised curriculum text, bypass NERDC portal controls, or label an unreviewed topic as NERDC verified.
- Do not upload student records or real child data into CI, fixtures, screenshots or public repositories.
- Keep the draft pull request open and unmerged until the owner requests otherwise.
- The existing university Telegram bot is out of scope and must remain untouched.

## Evidence record template

For every completed external gate, record: provider/authority; reviewer name and role; scope and version; date; evidence location with access restrictions; outcome; unresolved conditions; and the person who accepted the risk. Never place credentials or sensitive student data in this record.


## Engineering update — 7 November 2026

### Implemented and CI-verified on disposable fixtures
- Responsive administrator navigation, skip links, visible keyboard focus, reduced-motion/forced-colour support, and labelled student account fields.
- Curriculum source capture, draft topic mapping and publication workflow remain API-backed and role-gated; publication still depends on licensed evidence and teacher review.
- New administrator assessment authoring workspace and API: list/detail, create draft, add validated objective questions, role-gated publication and immutable published versions. Answer keys are never returned by assessment detail.
- Read-only finance ledger summary identifies transaction totals and unverified/stale exceptions; it does not contact Paystack or issue refunds.
- Student self-service JSON export and student data-rights request intake/withdrawal; restricted administrator review queue. Deletion requests are not automatically executed.
- Guarded local backup/restore rehearsal script and operational runbook.
- SMTP delivery contract tests with mocked STARTTLS/SSL transports; existing Paystack server-verification contract tests and private-audio S3/range/revocation tests remain in CI.
- Authenticated Playwright browser journeys run against a disposable PostgreSQL database with a synthetic owner administrator and synthetic subject fixtures.

### Exact-head CI evidence
Development commit `dd7b620676c4312aa9540a89d19be71381f71ec5` passed:
- [Push workflow 42415624459](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42415624459)
- [PR workflow 42415628254](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42415628254)

Both runs passed unit/security tests, JavaScript syntax checks, disposable PostgreSQL migration replay through 019, schema integration, assessment/payment E2E, synthetic student journey, authenticated/anonymous Playwright acceptance and non-publishing container build.

### Still blocked or requiring external evidence
- Live SMTP delivery/account recovery: no provider credentials or controlled mailbox delivery proof.
- Paystack sandbox: API contract tests pass; no authorised test account/key or provider-side charge/webhook/refund E2E evidence.
- Private audio: S3-compatible storage/range/security logic is mocked in tests; managed staging bucket has no media objects and no provider E2E playback/revocation proof.
- NERDC: no authorised curriculum corpus/licence and no independent subject-teacher signatures.
- Child safeguarding, guardian identity/consent, NDPA/DPIA, retention and legal review: drafts and technical request controls only; formal approvals absent.
- Backup/restore: guarded local rehearsal procedure is authored but no managed backup restore has been executed; RPO/RTO and retention remain unapproved.
- Monitoring: Render deployment/events can be inspected, but public /health response was not directly verified in this run; no alert delivery/incident drill evidence.
- Independent security review: not performed.

### Managed staging and deployment gate
- Managed Neon branch `think-tank-staging` contains migration history 001–013 only. Repository migrations 014–019 are CI-rehearsed but unapplied to managed staging.
- Render `learnwise-staging-api` remains on deployment `dep-dbn2dcrl550s73f9ahag`, commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`; auto-deploy is off. No deployment was triggered.
- PR #1 remains open/draft/unmerged. Main and the legacy university bot remain untouched.
- Staging migration/deployment approval and production-launch approval are separate explicit owner decisions. Neither has been granted.
