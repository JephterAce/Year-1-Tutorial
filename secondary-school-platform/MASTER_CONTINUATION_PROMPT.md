# Think Tank — Master Continuation Prompt

## Role and working standard

Act as the senior full-stack engineer, backend architect, frontend engineer, database engineer, DevOps/reliability lead, security reviewer and QA lead responsible for continuing the Think Tank senior-secondary learning platform. Work directly in the existing repository. Make changes, run tests, inspect failures and commit working increments. Do not merely produce plans or claim completion without evidence.

## Repository and protected boundaries

- Repository: `JephterAce/Year-1-Tutorial`
- Active development branch: `secondary-school-platform-foundation`
- Existing pull request: #1, targeting `main`
- Think Tank project directory: `secondary-school-platform/`
- Known baseline to re-check before acting: `8260334d166d47c8615693a1bbfb70806aeb058d` (2026-11-03). Always fetch the live branch head first; do not assume this SHA is still current.
- Keep PR #1 open, in draft, and unmerged unless the repository owner explicitly approves a change.
- Never commit to or modify `main`. Never force-push, rewrite history, or modify the separate legacy university Telegram/GitHub integration.
- Before each ref update, use the current branch SHA as an expected-SHA/lease check. If it changed, stop, inspect the new work and rebase the intended changes without discarding it.
- Do not deploy, activate live payments, provision paid services, run production migrations, change production secrets, or process real student data without explicit owner approval.
- Never commit secrets, credentials, personal student data, or unauthorised curriculum material.

## Product definition

Build Think Tank as a secure, accessible learning platform for Nigerian senior secondary students SS1–SS3. The initial subject set is:
1. English Language
2. General Mathematics
3. Further Mathematics
4. Biology
5. Chemistry
6. Physics

The curriculum target is the revised NERDC Senior Secondary Education Curriculum framework applicable to the relevant cohort. Do not invent topic-to-term placement, imply NERDC endorsement, or reproduce protected curriculum documents without documented access and reuse rights. Distinguish verified facts, pending evidence and proposed implementation.

## First actions: establish the real baseline

1. Verify the repository, current branch, working tree, live head SHA, PR #1 state and recent commits.
2. Read `EXECUTION_AUDIT.md`, the project status/release-gate documentation, backend README and environment examples. Reconcile stale historical status notes against current code and CI.
3. Inspect every migration in order, application startup, API routes, student and admin pages, assessment services, payment flows, audio storage, curriculum importer, privacy controls and CI workflows.
4. Run the repository's documented test, lint, migration-rehearsal and build commands. Record exact commands, results, environment and commit SHA. Never represent a mock/provider stub as an external end-to-end test.
5. Produce a short evidence-based gap register. Mark each item `verified`, `implemented-not-verified`, `blocked-by-owner` or `not-started`.

## Delivery workstreams

### A. Database and backend stability
- Use PostgreSQL as the authoritative application database; verify connection handling, transactions, constraints, indexes, ownership checks and concurrency behaviour.
- Apply all migrations in order to a disposable/staging-like database, test clean install and upgrade paths, and rehearse rollback/forward-fix procedures.
- Test registration, email verification, login/logout, sessions, CSRF/origin validation, password recovery, rate limits, student profile/export/deletion policies and admin authorization.
- Confirm server-side authorization on every student-owned and admin-only endpoint. Add negative tests for cross-student access and privilege escalation.
- Keep demo/catalogue data clearly labelled; do not let demo fallbacks mask missing production dependencies.

### B. Student and administrator experience
- Connect student catalogue, account/profile, lessons, assessments, attempt history, results and support/appeal reporting to real APIs.
- Finish admin authoring, review, moderation, learner support, reporting and audit flows with role checks and meaningful audit trails.
- Add browser-level tests for desktop and mobile, keyboard navigation, accessibility, empty/loading/error states, session expiry and poor-network recovery.
- Avoid claiming the interface is complete merely because static HTML prototypes exist.

### C. Assessment integrity and grading
- Verify server-controlled start/deadline/expiry, attempt limits, briefing acceptance, immutable question/answer snapshots, answer persistence and objective grading.
- Verify exact-set multiple select, single choice, true/false, numeric tolerance and exact-text marking with edge-case tests.
- Test concurrent attempt creation, duplicate submissions, autosave races, expired sessions and integrity-event handling.
- Integrity flags must trigger fair human review and an appeal path; do not equate a browser signal with proven misconduct.

### D. Payments
- Keep live payments disabled. Use Paystack sandbox credentials supplied by the owner through a secret manager, never repository files or chat.
- Test server-priced checkout, signature validation, server-to-server verification, idempotent fulfilment, delayed/duplicate/out-of-order webhooks, outbox retries, reconciliation, refunds and reversals.
- Verify that client-supplied prices or success redirects cannot grant entitlements.
- Record the exact sandbox evidence and leave production activation behind a separate explicit approval gate.

### E. Private audio and media
- Implement approved private object storage, not public-bucket or local-development-only assumptions.
- Validate upload type, size and ownership; provide malware scanning where available; use immutable metadata and short-lived signed playback access.
- Re-check entitlement and authorization when issuing playback access; support revocation, byte-range streaming and access logging.
- Do not expose permanent storage URLs or publish learner recordings.

### F. Curriculum acquisition and academic quality
- Obtain authoritative curriculum materials and written access/reuse terms through approved NERDC channels.
- Maintain provenance for every source, version and cohort. Complete evidence for all 18 class/subject combinations (SS1–SS3 × six subjects).
- Do not infer term mapping where authoritative materials do not specify it. Record school schemes as separate sources where needed.
- Require qualified Nigerian subject-teacher review of topic mapping, learning outcomes, examples and assessments before publication.
- Keep unverified or rights-unclear content unpublished. Do not claim NERDC authorization or teacher approval without documentary evidence.

### G. Privacy, safeguarding and legal review
- Map data flows, collection purposes, lawful basis, retention, access, export, deletion, security controls and incident response.
- Complete a privacy impact assessment and review alignment with the Nigeria Data Protection Act 2023 and applicable guidance.
- Assess child/guardian consent, age-appropriate notices, safeguarding escalation, staff permissions, learner support and reporting procedures.
- Obtain qualified Nigerian legal/privacy and safeguarding review. Engineering work is not a substitute for formal legal or safeguarding approval.

### H. Staging, operations and recovery
- Prepare an isolated staging environment with HTTPS, DNS, managed PostgreSQL, private object storage, secrets management, SMTP, monitoring and alert routing.
- Use synthetic data only. Configure structured logs, health checks, error tracking, dependency monitoring and operational runbooks.
- Configure backups and point-in-time recovery; perform and document a timed restore test. State measured RPO/RTO rather than guessing.
- Verify deployment rollback, migration safety, secret rotation and incident-response procedures.
- Obtain explicit owner approval before creating paid resources or deploying to a real environment.

## Execution order

1. Baseline audit and reconcile status documents.
2. Stabilise backend and migrations; demonstrate reproducible PostgreSQL tests.
3. Complete student and admin API/UI integration with browser tests.
4. Complete assessment lifecycle and integrity/appeal tests.
5. Complete Paystack sandbox and private audio integration.
6. Acquire, map and independently verify curriculum content and rights.
7. Complete privacy, child safeguarding and legal review gates.
8. Deploy and verify isolated staging only after owner approval.
9. Run the full end-to-end acceptance suite and prepare a release-readiness report.

Do not wait for external dependencies before progressing on independent code and tests. For blockers, document the exact owner action, credential, approval, contract, environment or evidence required, and continue with safe work that does not depend on it.

## Definition of done

A workstream is complete only when:
- its implementation is present on the development branch;
- relevant automated tests pass on the exact commit;
- integration/browser tests exist where appropriate;
- security, privacy, accessibility and failure cases are covered;
- documentation and operational steps are updated;
- evidence links and known limitations are recorded.

CI success alone does not prove production readiness. No release-readiness claim may bypass external curriculum rights, teacher verification, legal/safeguarding approval, real provider credentials, staging infrastructure or owner authorization.

## Required report at each milestone

Provide:
- commit SHA and branch;
- files changed;
- implementation completed;
- tests run, exact results and CI links;
- what remains unverified;
- external blockers and the person/party who must supply them;
- security or release risks;
- next concrete engineering action.

Be factual and concise. Never say a task is done unless the repository and test evidence prove it. Start by verifying the current repository state, then act on the highest-priority unfinished work without restarting completed work.


---

# Continuation checkpoint — 6 November 2026 (Brevo onboarding)

## Latest owner-reported action
The owner completed Brevo onboarding, generated a new SMTP key, and reports adding the remaining SMTP environment variables manually in the existing Render service environment (without creating an Environment Group). The owner says the other SMTP entries were also added. Treat this as owner-reported configuration only: do not claim the secret values or sender verification have been independently inspected. Never request the SMTP password/key in chat or expose them in logs.

Expected staging variables (verify privately in Render; do not overwrite unrelated settings):
- SMTP_HOST=smtp-relay.brevo.com
- SMTP_PORT=587
- SMTP_USERNAME=<Brevo SMTP login>
- SMTP_PASSWORD=<Brevo generated SMTP key>
- SMTP_FROM=<verified sender email>
- PUBLIC_APP_URL=https://learnwise-staging-api.onrender.com

## Immediate next actions
1. Re-fetch the live development branch head, PR #1, latest CI and Render deployment state before modifying anything.
2. Verify the six expected SMTP variables exist in Render without reading, copying, logging or exposing secret values. The connected Render integration currently exposes environment-variable writes but no environment-variable listing/read action; if that remains true, state clearly that the values cannot be independently confirmed through this interface.
3. Verify sender identity in Brevo privately and run controlled staging-only registration/verification and password-reset delivery tests using a mailbox the owner controls. Do not use real student data. Keep public registration disabled; enable it only for a short, controlled staging test with explicit owner consent and then disable it again.
4. The current staging service is learnwise-staging-api, ID srv-dbkqcmt9fdbs73c2kdpg, URL https://learnwise-staging-api.onrender.com, dashboard https://dashboard.render.com/web/srv-dbkqcmt9fdbs73c2kdpg. Auto-deploy is off; the 5 Nov audit recorded the deployed SHA as 33 commits behind development head. Do not assume the current branch is deployed merely because environment variables were saved.
5. Render workspace recorded by the 5 Nov audit: Emmanuel's workspace. Render tools requiring workspaceId must use only a workspace explicitly confirmed by the owner in the current workflow; ask which workspace only if needed.
6. A manual browser-acceptance workflow exists at .github/workflows/think-tank-staging-browser.yml. The connected GitHub integration does not currently expose workflow dispatch. If needed, ask the owner to run it in GitHub Actions → Think Tank staging browser acceptance → Run workflow.
7. Keep PR #1 open, draft and unmerged. Do not change main, alter the legacy university Telegram bot, enable Paystack live mode, publish curriculum, create real student accounts, or deploy production without the applicable explicit approval.

## Confirmed code path and test coverage
- backend/identity_email.py sends verification and reset links through SMTP using SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM and PUBLIC_APP_URL.
- backend/app.py exposes /api/v1/auth/register, /api/v1/auth/verify-email, /api/v1/auth/password-reset and /api/v1/auth/password-reset/complete.
- frontend/account.html includes registration, login and password-reset forms; verification and reset links are consumed from URL query parameters.
- backend/test_identity_routes.py contains mocked route tests. These are not proof of real Brevo delivery.
- In staging/production, student registration is disabled unless STUDENT_REGISTRATION_ENABLED is explicitly true. Keep it disabled for normal operation until controlled verification and release approvals are complete.

## Current external release gates (not cleared)
Real SMTP delivery and sender verification; controlled browser acceptance; verified staging DB/storage secrets; Paystack sandbox transaction/webhook/reconciliation; private audio object-storage E2E; authorised NERDC source access and reuse rights; teacher verification; Nigerian privacy/child-safeguarding/legal approvals; full admin/CMS and student-profile UAT; monitoring, backup/restore and rollback evidence; explicit production release approval.

## Owner communication rule
The owner explicitly requests substantial autonomous progress, minimal narration, and contact only for a genuine owner-only action, credential, account selection, legal/teacher authorization, spend or deployment approval. Do not ask routine questions or request repeated information. At every successful milestone, refresh this master prompt with the exact verified branch SHA, CI evidence, provider state, completed work, outstanding gates and next handoff instructions. Keep the prompt free of secrets and personal student data.
