# Think Tank execution audit

**Audit date:** 2026-11-02  
**Repository:** `JephterAce/Year-1-Tutorial`  
**Branch:** `secondary-school-platform-foundation`  
**Pull request:** #1 (draft, open, unmerged)  
**Audit baseline:** `001ce6dc4b47bd69ca4e4552b552557b72b92185`  
**Audit scope:** all 103 files changed by PR #1; recursive branch tree contained 116 entries (including root-level files and directories).

## Executive decision

The repository contains a substantial implementation foundation. It is **not approved for production or public student onboarding**. CI passed on the audit baseline, including PostgreSQL 16 migration replay, database integration, assessment/payment E2E with provider-shaped stubs, frontend/admin JavaScript syntax checks, and a non-publishing container build. These checks do not substitute for live provider credentials, a managed database, independent review, or staging acceptance.

## Stage 1 — Repository audit

### Inventory verified

- 13 ordered SQL migrations (001–013).
- Flask backend, PostgreSQL repository, student identity/session services, profile/export services, assessment attempt/grading/reporting services, admin authentication/review services, payment order/outbox/Paystack verification/webhook services, curriculum importer, and private-audio token/path module.
- Student pages: catalogue/dashboard, account, assessment, lesson.
- Admin pages: workspace prototype and protected assessment-review console.
- CI workflow, Dockerfile, disposable PostgreSQL rehearsal Compose file, operational and release-gate documentation.

### Defects and limitations found

1. The local `app.py` startup guard appeared before later route declarations. Direct `python app.py` execution could start the server before those routes were registered. Corrected on the branch in commit `c62354310d9252d8b1e2d69ae1ac7ffcbe2bcc34`; the new commit's CI run was queued at audit time.
2. Documentation across STATUS and release-gate records contains historical snapshots that do not all describe the current branch head. This audit records the newer verified CI evidence and should be used alongside, not confused with, historical notes.
3. CI runs migrations and E2E tests only against disposable PostgreSQL 16 infrastructure. No dedicated managed staging/production database is connected.
4. The Docker workflow builds but does not publish or deploy an image.

## Stage 2 — Backend stabilisation

**Verified in repository/CI**
- Numbered migrations 001–013 replay successfully on a clean disposable PostgreSQL 16 database.
- PostgreSQL schema integration and assessment/payment database E2E tests pass on the audit baseline.
- Student registration, email verification, login/logout, session/CSRF checks, password reset, student profiles, assessment attempt lifecycle, objective grading, issue reporting, admin authentication/review, payment webhook verification and outbox foundations are present.
- CI run #503 on commit `001ce6dc4b47bd69ca4e4552b552557b72b92185` passed both jobs.

**Still required**
- Provision a dedicated managed PostgreSQL staging database; configure TLS, least-privilege roles, backups and monitoring.
- Rehearse migration and rollback/forward-fix procedures against a staging-like snapshot.
- Configure real SMTP delivery and test verification/reset, retries and abuse controls.
- Conduct concurrency, session lifecycle, origin/CSRF, proxy-aware rate-limit and independent security testing.
- Verify all admin operations and audit controls against the real database.

## Stage 3 — Student and admin experience

**Implemented foundations**
- Student catalogue, account/profile, lesson and assessment pages exist.
- Student profile, assessment attempt/history and issue-report APIs are described as connected in the current STATUS record.
- Admin login and protected assessment-review console exist.

**Still required**
- Full browser/mobile end-to-end acceptance across registration, sign-in, catalogue, lesson entitlement, playback, assessment, results and support.
- Complete CMS/content authoring and curriculum publishing workflow.
- Admin finance/payment reconciliation workflows and operational dashboards.
- Profile photo upload/storage and profile visibility changes remain disabled.
- Accessibility, device/browser compatibility and poor-network recovery acceptance.

## Stage 4 — Payments and audio

**Implemented foundations**
- Server-priced Paystack order/checkout primitives, raw-body webhook signature validation, server-side verification, idempotent fulfilment and notification outbox/worker code.
- CI uses synthetic data and provider-shaped stubs; the latest baseline E2E workflow passed.
- Short-lived HMAC audio tokens and private local-storage path confinement are implemented.

**Still required**
- Owner configures Paystack sandbox credentials directly in a secret manager; execute real sandbox charge, webhook delivery/retry, duplicate/delayed event, failure, reconciliation and refund/reversal scenarios.
- No live payment credentials or real provider transaction has been tested.
- Add approved private object-storage adapter, upload validation/malware scanning, immutable object metadata, byte-range streaming, entitlement recheck/revocation and storage monitoring.
- No production object-storage provider or real approved audio asset corpus is configured.

## Stage 5 — Curriculum, privacy and safeguarding

**Implemented foundations**
- Versioned curriculum/source provenance and rights metadata, import template/validator and evidence-gated publication controls.
- Privacy notice, terms, safeguarding/legal review register and data-export foundations.
- Curriculum source register and acquisition workflow.

**Release blockers**
- Obtain authorised NERDC materials and explicit reuse/licensing permissions through the approved route.
- Complete source evidence for all 18 selected class/subject combinations; do not infer class, cohort or term placement.
- Obtain independent qualified Nigerian subject-teacher verification before publication.
- Complete Nigerian privacy/legal review, DPIA, child/guardian consent assessment, retention/deletion and breach processes.
- Appoint a safeguarding lead, approve escalation process, staff access controls and learner-support procedures.
- No legal, safeguarding or NERDC approval is represented as obtained.

## Stage 6 — Staging deployment

**Implemented foundations**
- Non-root Gunicorn Docker image, health endpoint, disposable PostgreSQL Compose environment and deployment/operations runbook.
- CI container build succeeds without publishing.

**Still required**
- Owner selects and authorises hosting, managed PostgreSQL, private object storage and secret manager.
- Provision isolated staging with HTTPS, DNS, monitoring, alert routing, structured logs and synthetic data only.
- Configure and verify backups, point-in-time recovery and a timed restore exercise; document RPO/RTO.
- Run staging browser, API, payment sandbox, audio entitlement, accessibility, security and incident-response tests.
- Obtain explicit owner approval before staging deployment. Production remains separately gated.

## Current CI evidence

- Run #503, commit `001ce6dc4b47bd69ca4e4552b552557b72b92185`: successful.
- Run URL: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/41400544761
- The direct-startup fix commit `c62354310d9252d8b1e2d69ae1ac7ffcbe2bcc34` passed CI (run 41403284904). The audit document commit `83db267f71dbcbe4bd4bd28db222d032668a7c66` also passed CI (run 41403318357).

## Safety and change control

- Keep PR #1 draft and unmerged until the owner requests review/release.
- Do not deploy, run production migrations, activate live payments, buy services, or change production secrets without explicit owner approval.
- Never commit credentials, student data, or unauthorised curriculum content.
- Keep the separate legacy university bot and `main` branch untouched.

## Hardening pass (Stage 2, from branch commit 3b232fd)

- **Attempt-limit bypass fixed:** `start_attempt` now takes a per-student lock and rechecks `max_attempts`; `create_attempt` reuses an open briefing instead of creating unlimited rows.
- **Overdue attempts** are now scored once, on first view (`get_attempt`), not only on save/submit.
- **Answer size caps** (text 500 chars; 20 selections of 100 chars) in `check_answer_size`.
- **Security headers** on all responses (nosniff, X-Frame-Options, Referrer-Policy, no-store on /api, HSTS in staging/production).
- **UI layer:** `frontend/think_tank-ui.css` adds dark mode, mobile bottom navigation, focus rings, 44px touch targets and reduced-motion support.
- Tests: `test_attempt_hardening.py`. 153 unit tests pass locally (PostgreSQL tests require CI).
- **Open:** entitlement enforcement on attempts; admin student/curriculum/payment consoles; per-IP rate limiting; live Paystack sandbox, SMTP, managed PostgreSQL and object storage (Issue #2).

## Entitlement gate (patch 2)
- `create_attempt` can now require an active, unrevoked entitlement on a published topic of the assessment's subject and class (HTTP 402 `entitlement_required`).
- Controlled by `ASSESSMENT_REQUIRES_ENTITLEMENT=1`; **off by default** so existing behaviour is unchanged. Decide the product rule (paid-only vs free assessments) before enabling in staging.
- Unit-tested: flag behaviour only. The SQL path needs the PostgreSQL E2E job (not run locally).


## Continuation audit — 8 November 2026

### Render / Neon verification
- Confirmed Emmanuel's Render workspace (`tea-da2svh0ae00c73cs4qq0`) and inspected service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`). Latest deployment `dep-dbo22jp5efls73cm1sb0` is live at `c5805a6fc463fd040e64e8223d58ed3dbf37d143`; auto-deploy remains disabled and no new deployment was triggered.
- GitHub Actions staging-health job verified `/health` with HTTP 200 and JSON status=ok, mode=database, service=secondary-school-api. Render logs show Gunicorn workers started and the service is live.
- Read-only Neon queries confirmed managed staging migration history 001–019 and exact GitHub blob SHA matches for all 19 applied migrations. Counts: 6 subjects, 0 topics, 0 students, 1 active admin, 0 data-rights requests.
- Verified backup branch `br-super-haze-bazf13ia` and isolated migration rehearsal branch `br-divine-bread-bah58gvn` are ready.

### New implementation: private admin data exports
- Added migration 020 `020_private_student_export_approval.sql` with a separate approver, approval timestamp, manifest object key, worker start/attempt metadata, distinct-approver constraint, attempt cap and approved-queue index.
- Added `student_bulk_export.py` for a repeatable-read/read-only snapshot, server-side cursor, streamed NDJSON/CSV, multipart S3-compatible upload, SHA-256 manifest, bounded export size, five-minute signed URL cap and expiry cleanup.
- Added `admin_data_exports.py` routes for request, list, approve, retry, cancel and download. Requests are rate-limited; bulk requests require explicit confirmation and class/date scope; subject filters fail closed. Requester cannot approve their own job.
- Added `/admin/exports` restricted admin UI and navigation. Added separate DATA_EXPORT_AWS_* configuration placeholders; the worker remains disabled by default and requires a dedicated private bucket.
- Updated student export builder to reuse the worker's repeatable-read connection rather than opening a separate connection per student.
- Added worker and route tests. The first CI run containing these tests (42459497431 at e7f4d41) passed staging-health and non-publishing container-build, but API tests failed on two test fixtures missing `export_scope`. The fixtures were corrected at `df88729f54cf34353943c144de784453da46d23d`; subsequent changes further hardened worker transaction boundaries, empty uploads, expiry, locking, partial-object cleanup and request caps. A fresh exact-head CI result is not yet available; no pass is claimed.

### Isolated migration 020 rehearsal
- Applied migration 020 only to Neon rehearsal branch `br-divine-bread-bah58gvn`, not managed staging.
- Read-only schema inspection confirmed six new columns, four new check constraints, the approver foreign key and the approved-queue index.
- Added rehearsal history entry `020_private_student_export_approval` with source blob SHA `3ee86c0d909f429f6ca5787c47b51f86dfdf9a13`, matching the development branch migration file.
- Managed staging remains at migration 019. Migration 020 requires explicit owner approval before staging application.

### Remaining blockers / change control
- Only one active owner admin exists on staging. Two-person export approval cannot be completed until a second owner is provisioned through the controlled offline process.
- No dedicated data-export bucket, credentials, worker schedule or real export job exists. Worker remains disabled.
- Staging has zero curriculum topics and zero students. Authorised NERDC material/licensing and teacher review are prerequisites to content population.
- SMTP delivery/password recovery, Paystack sandbox E2E, private audio storage/playback, child safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, managed backup restoration/RPO/RTO, monitoring/incident alerting and independent security review remain outstanding.
- PR #1 remains open/draft/unmerged; `main` and production remain untouched. No new Render deployment or managed staging migration was performed.


### CI correction — 8 November 2026
- Workflow 42460006986 (commit 1316c1d2fa789c2f67eb389ac10605f0489ac374) ran 260 unit/security tests successfully; staging-health passed; non-publishing container build passed.
- The syntax step found one inline JavaScript parse error in admin/exports.html: a literal escaped newline between the DOM helper and currentAdminId declaration. Fixed in commit 81d33094f0506a71c9f72984133075fa75c84252. Read-back verifies the literal sequence is gone and a real newline is present.
- No new exact-head CI run is yet available after the fix. PostgreSQL migration replay, backup restore, schema integration, payment/student E2E and authenticated browser tests were skipped in run 42460006986 because syntax checking failed. Do not mark the new feature release-ready until a fresh exact-head run completes all steps.


### Full disposable CI pass and export-browser acceptance in progress — 8 November 2026
- Run 42460191786 (run 1180, commit 7de9dd1d0da160e634673fc813a16befb147e383) completed successfully across API tests, staging health and container build. It passed 260 unit/security tests, Python/JS/shell syntax, all 20 numbered migrations and idempotency, local backup/restore, PostgreSQL schema integration, assessment/payment E2E, registration-to-results and the existing authenticated/anonymous browser suite.
- Run 42460225765 (run 1184, commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) adds the new export workspace Playwright test (queue/cancel and no self-approval) and anonymous exports page redirect. Unit tests, syntax, migration replay, backup/restore, PostgreSQL integration, assessment/payment E2E and student journey all passed; Playwright was still installing/running at the latest check.


### Full exact-code CI verification — 8 November 2026
- Run 42460225765 (run 1184) at code commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3 completed green across API tests, staging health and container build.
- Verified 260 unit/security tests; Python/frontend-admin JavaScript/shell syntax; all 20 numbered migration replays and idempotency; guarded local backup/restore; PostgreSQL schema integration; assessment/payment E2E; registration-to-results; anonymous/authenticated Playwright suite. New export acceptance verified the restricted page, queued filtered bulk request, requester cancellation and no self-approval button. Anonymous visitors are redirected from /admin/exports.
- Public staging health returned HTTP 200 with status=ok, mode=database, service=secondary-school-api. Container build was non-publishing.
- The tested code commit is included in the current development branch; subsequent commits only update docs. No code was deployed. Managed staging remains at 019; migration 020 remains isolated.
