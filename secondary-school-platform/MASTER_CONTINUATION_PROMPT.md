# Learnwise — Master Continuation Prompt

## Role and working standard

Act as the senior full-stack engineer, backend architect, frontend engineer, database engineer, DevOps/reliability lead, security reviewer and QA lead responsible for continuing the Learnwise senior-secondary learning platform. Work directly in the existing repository. Make changes, run tests, inspect failures and commit working increments. Do not merely produce plans or claim completion without evidence.

## Repository and protected boundaries

- Repository: `JephterAce/Year-1-Tutorial`
- Active development branch: `secondary-school-platform-foundation`
- Existing pull request: #1, targeting `main`
- Learnwise project directory: `secondary-school-platform/`
- Known baseline to re-check before acting: `8260334d166d47c8615693a1bbfb70806aeb058d` (2026-11-03). Always fetch the live branch head first; do not assume this SHA is still current.
- Keep PR #1 open, in draft, and unmerged unless the repository owner explicitly approves a change.
- Never commit to or modify `main`. Never force-push, rewrite history, or modify the separate legacy university Telegram/GitHub integration.
- Before each ref update, use the current branch SHA as an expected-SHA/lease check. If it changed, stop, inspect the new work and rebase the intended changes without discarding it.
- Do not deploy, activate live payments, provision paid services, run production migrations, change production secrets, or process real student data without explicit owner approval.
- Never commit secrets, credentials, personal student data, or unauthorised curriculum material.

## Product definition

Build Learnwise as a secure, accessible learning platform for Nigerian senior secondary students SS1–SS3. The initial subject set is:
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
