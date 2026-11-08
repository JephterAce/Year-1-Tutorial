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


### Additional authenticated student acceptance — 7 November 2026

Latest tested application commit a057289c4930b86b6bdd5176bd71e61a9536f044 passed exact-head push [42416064502](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416064502) and PR [42416068375](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416068375).

The suite passed 246 unit/security tests, Python/JavaScript/shell syntax checks, baseline plus migrations 001–019 on disposable PostgreSQL, schema integration, assessment/payment E2E, synthetic registration-to-results, non-publishing container build and 14 Playwright tests. The browser tests include a real authenticated synthetic student session, data-rights request submission/withdrawal, own-data JSON download and secret/answer-key exclusion assertions. No managed staging data was touched.


### Managed staging migration checksum comparison — 7 November 2026
All 13 applied migration source_blob_sha values in managed Neon learnwise_migration_history exactly match the GitHub blob SHAs of canonical backend migrations 001–013 on the development branch (13/13). This is a read-only source-integrity comparison. Migrations 014–019 remain unapplied; clean disposable CI replay is not a substitute for an isolated upgrade rehearsal from the managed 001–013 state.


### Public staging health and restore verification — 7 November 2026

Current branch head ee2cc4306279772ecb05a3813eb33266c134d497 passed exact-head push [42416698937](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416698937) and PR [42416702456](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416702456).

A read-only CI health job verified public Render /health returns HTTP 200 and JSON status=ok, mode=database, service=secondary-school-api. The CI workflow now performs this check on every push/PR run. The same workflow successfully completed a local pg_dump/pg_restore rehearsal to a separate disposable PostgreSQL database and verified all 20 baseline-plus-migration history entries were restored. This does not replace managed backup/PITR or production restore evidence.

Managed Neon still has only 001–013 (all 13 source blob hashes match); 014–019 remain unapplied. Render remains on its previous live SHA and no deployment was triggered.


### Latest branch head — 7 November 2026

Current branch head 1419ed4b8c6011ad5d30ea9299a36c2816e1aa3c passed exact-head push [42416831355](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416831355) and PR [42416833832](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416833832). Both include public staging health verification (HTTP 200/status=ok/database/secondary-school-api), 246 unit/security tests, disposable PostgreSQL migration/schema and E2E suites, local backup/restore rehearsal, authenticated/anonymous Playwright acceptance and non-publishing container build.


### Final documentation-head confirmation — 7 November 2026
Repository/PR head 2098d7ad37b830a84a1120654afc56b5152ae4ef passed exact-head push [42416959890](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416959890) and PR [42416965208](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42416965208). Latest tested application commit remains a057289c4930b86b6bdd5176bd71e61a9536f044; the later head updates documentation/PR evidence only.


### Handover pointer — 7 November 2026
Current branch/PR head fc77dbc714af2103b50f58c02bff844556a776ad passed exact-head push 42417089283 and PR 42417094553. Application code tested at a057289c4930b86b6bdd5176bd71e61a9536f044; later commits update workflow and documentation evidence only. Public staging health passed HTTP 200/status=ok/mode=database/service=secondary-school-api.


### Engineering continuation and release-gate reconciliation — 8 November 2026

- Current work remains on the development branch and draft PR #1. The latest Render deployment is live at commit c5805a6fc463fd040e64e8223d58ed3dbf37d143; Render auto-deploy is off. No deployment of the newer export work was triggered.
- Public staging health was independently verified by GitHub Actions on the 7 November run: HTTP 200, JSON status=ok, mode=database, service=secondary-school-api. The 8 November Render deploy itself also completed successfully and the service booted Gunicorn workers.
- Managed staging migration history contains exactly 001–019; all 19 source_blob_sha values match the canonical migration file blob SHAs. Staging remains unchanged by this continuation.
- Additive migration 020_private_student_export_approval.sql was rehearsed only on isolated Neon branch br-divine-bread-bah58gvn. Column, constraint and index inspection passed; its rehearsal history row matches the development migration blob SHA. Migration 020 is not applied to managed staging.
- New development-branch work adds admin export request/approval/download routes, a restricted admin page, a streaming worker, private bucket configuration placeholders, checksum manifest, five-minute signed links, 24-hour default expiry, retry/cancel controls, request caps and two-person approval. Subject-scoped bulk exports fail closed. The worker remains disabled; no export bucket, credentials or schedule exists.
- Two-person export approval is not currently usable: managed staging has one active owner admin. A second authorised administrator must be provisioned offline before any admin export can be approved. No bypass is permitted.
- The latest read-only staging counts are 6 subjects, 0 topics, 0 students, 1 active admin and 0 data-rights requests. Curriculum population cannot proceed until authorised source materials, rights and teacher review are established.
- The first CI run that included the new export tests (run 42459497431, commit e7f4d41) passed staging-health and non-publishing container-build jobs but the API test job failed on two new test fixtures missing export_scope. The fixture was corrected in subsequent branch commits. No later exact-head CI result is currently available; do not mark the new export code as CI-passed until a fresh run completes.

#### External / owner-controlled gates still open
- SMTP delivery and password/account recovery end-to-end verification.
- Paystack sandbox end-to-end checkout, webhook, entitlement and reconciliation.
- Private audio bucket configuration, real approved test asset, entitlement playback and range/expiry acceptance.
- Authorised NERDC materials/licensing, curriculum mapping, teacher review and publication; staging currently has zero topics.
- Child safeguarding, guardian consent, age verification, NDPA assessment/DPIA and retention schedule.
- Nigerian legal review of terms, privacy, child data, payment and retention obligations.
- Managed backup/PITR restoration drill, measured RPO/RTO and recovery-owner sign-off.
- Monitoring, incident-alert delivery and incident-response rehearsal.
- Independent security review and remediation evidence.
- Dedicated private data-export bucket, second active export approver, scheduled worker/expiry cleanup and subject-scoped export support.

Production remains blocked. Do not merge PR #1, deploy the new branch, apply migration 020 to managed staging, provision billable services, or claim launch readiness until the relevant tests, external evidence and explicit owner approvals are recorded.


### Corrected admin export page syntax — 8 November 2026
- Exact-head workflow 42460006986 at commit 1316c1d2fa789c2f67eb389ac10605f0489ac374: 260 unit/security tests passed; staging-health passed HTTP 200/status=ok/database/secondary-school-api; non-publishing container build passed.
- Syntax check failed on a literal escaped newline in admin/exports.html. Fixed in commit 81d33094f0506a71c9f72984133075fa75c84252 and confirmed by reading back the updated source.
- A fresh exact-head workflow run has not yet been returned for the corrected commit. Migration replay, backup/restore, PostgreSQL schema/E2E and authenticated browser steps remain unverified for this increment. Keep migration 020 and the matching code deployment blocked pending a full green run.


### Full CI pass and latest export browser test — 8 November 2026
- Run 42460191786 (run 1180, commit 7de9dd1d0da160e634673fc813a16befb147e383) completed fully green: API tests, staging health and container build. It verified 260 unit/security tests, syntax, 20 numbered migration replays/idempotency, backup/restore, PostgreSQL schema integration, assessment/payment E2E, student journey and existing browser acceptance.
- Run 42460225765 (run 1184, commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) includes new export-workspace browser coverage and anonymous /admin/exports access checks. All steps through student journey passed; Playwright installation/browser acceptance remained in progress at the latest inspection. Keep the export UI acceptance gate open until that run completes.


### Green full CI and export workflow acceptance — 8 November 2026
- Run 42460225765 (run 1184, code commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) is fully green across API tests, staging-health and non-publishing container-build.
- Passed 260 unit/security tests, syntax checks, all 20 numbered migration replays/idempotency, backup/restore, PostgreSQL schema integration, assessment/payment E2E, student journey and anonymous/authenticated browser acceptance. The added private-export browser scenario passed: an owner can queue a filtered bulk request, cancel it, and cannot approve their own request; anonymous access redirects to admin login.
- This does not verify live SMTP, Paystack, private audio, NERDC content rights, child-safeguarding/legal controls, managed backup/PITR, alert delivery, independent security review or a real private export bucket/worker. It also does not deploy the code or apply migration 020 to managed staging.


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


### Latest staging diagnostic deployment — 8 November 2026, 12:58 WAT
- Improved SMTP failure-phase observability is now deployed to staging in Render deployment `dep-dbo67aajnfac73e0kt2g`, commit `fa8d3377aac13068cc17801874c85a48c504a9e4`; Render status `live`.
- Exact-commit GitHub Actions run [42474098220](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42474098220) completed successfully: API/security suite, post-deploy staging health, and non-publishing container build. PostgreSQL migration/schema, assessment/payment, student journey, browser acceptance and disposable backup/restore rehearsals passed in the API job.
- The diagnostic now records only a bounded failure phase and exception class. No provider details or secrets are logged. The owner-reported SMTP attempt remains failed/unverified; no retry was made. Brevo delivery is not cleared.
- No PR merge, `main` change, production deploy, public registration, or live payment occurred.

### Draft sign-off templates — not approvals
Use the following records to collect actual accountable human sign-off. A blank or unsigned template does not clear a release gate. Attach evidence, date, reviewer identity/qualification, scope, exceptions and expiry/review date to each signed record.

#### Subject-teacher curriculum review (repeat for each of the 18 class/subject combinations)
- Class: SS1 / SS2 / SS3
- Subject: English Language / General Mathematics / Further Mathematics / Biology / Chemistry / Physics
- Teacher name and qualification:
- Evidence of subject/teaching competence:
- Curriculum/source version and source URL/reference:
- Rights/licence and permitted reuse confirmed (yes/no; evidence):
- Topic sequence, learning outcomes and assessment alignment reviewed (yes/no):
- Corrections or exclusions required:
- Decision: approve / approve with conditions / reject
- Signature and date:

#### Safeguarding lead appointment and review
- Appointed lead and organisation:
- Relevant safeguarding experience/training:
- Reporting/escalation contact and deputy:
- Child-safety policy, moderation, staff conduct and incident-response procedures reviewed:
- Risk assessment and unresolved risks:
- Decision and conditions:
- Signature and date:

#### Guardian consent and child-data processing approval
- Legal basis and purpose for each data category:
- Guardian identity/authority verification method:
- Child-appropriate notice and guardian notice version:
- Separate consent choices (account, learning records, communications, audio/media where applicable):
- Withdrawal, access, correction and deletion route:
- Retention/deletion schedule:
- Consent evidence location and access restrictions:
- Safeguarding escalation and complaints route:
- Approved by safeguarding/privacy owner; date/version:

#### NDPA/DPIA and Nigerian legal review
- Qualified Nigerian counsel/privacy reviewer and credentials:
- Controller/processor roles and vendor/subprocessor list:
- Data inventory, purposes, lawful bases, data flows and cross-border transfers:
- Necessity/proportionality, child-specific risks and mitigations:
- Security controls, breach response, rights handling and retention:
- Required notices/contracts/registrations identified:
- Opinion: approved / conditional / not approved; conditions:
- Signed report reference and date:

#### Second administrator appointment
- Full name and verified organisation email (record outside public repository):
- Role and least-privilege permissions:
- Identity verification and MFA confirmed:
- Training on two-person export approval, audit logs and incident escalation:
- Appointment approved by owner; date:
- Acceptance by appointee; date:

#### Independent security review
- Independent reviewer/firm and conflict-of-interest declaration:
- Scope: application, authentication, authorisation, child data, APIs, storage, payments, deployment and incident response:
- Test environment and written authorisation reference:
- Findings by severity and evidence:
- Remediation owner and retest evidence:
- Residual-risk acceptance by accountable owner:
- Final opinion and date:

#### Backup, monitoring and operational acceptance
- Approved RPO/RTO, retention, recovery owner and budget:
- Managed backup/PITR source and restore target:
- Isolated restore evidence, integrity checks and measured RPO/RTO:
- Alert recipient/on-call owner and escalation path:
- Synthetic alert sent/received/acknowledged timestamps:
- Operational runbook owner and review date:
- Approval and date:

These templates are preparatory only. They do not constitute legal advice, guardian consent, teacher endorsement, provider verification, or independent assurance. Public student onboarding and production release remain blocked until the applicable evidence is completed and the owner separately authorises release.


## Current verified staging checkpoint — 8 November 2026, 16:51 UTC

- Current branch head d66cca79bb12221de7228ffc8b49e4b5167f6f66; PR #1 remains draft/open/unmerged; main unchanged.
- Application deployment dep-dboaenuc6qcc73d3lc00 is live on a9b7bacd4c3069651319df79ce95ec932a7797fc. Push CI 42501847900 and PR CI 42501852204 passed; live read-only browser 42501847936 passed 10/10. Staging health returned HTTP 200 / status=ok / mode=database / service=secondary-school-api.
- Synthetic QA lifecycle is implemented, migration 021 applied and CI-tested. Owner-only create/revoke/expiry controls are enabled in staging; no synthetic account has been created. Owner invitation/verification and authenticated live acceptance remain outstanding.
- Owner-only storage acceptance endpoint/UI is enabled in staging. It performs synthetic private audio and R2 PUT/GET/checksum/unsigned-denial/DELETE from the Render runtime. The probe has not yet been run. Cloudflare R2 inventory shows one bucket only and r2.dev disabled; both Neon storage buckets are private. Cross-bucket denial remains outstanding without a second R2 bucket/credential.
- Public student registration, export worker and live payments remain disabled. Staging database has zero student rows, zero synthetic QA rows, one active admin, zero approved curriculum sources and zero topics.
- Still release-blocking: actual SMTP delivery/account recovery; owner-run storage and synthetic QA acceptance; Paystack sandbox; licensed curriculum and qualified teacher review; safeguarding/guardian consent/NDPA/DPIA; Nigerian legal review; managed backup restoration/RPO/RTO; monitoring alert delivery; second administrator; independent security review. Production remains NOT READY.

