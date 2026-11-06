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


---

# Continuation checkpoint — 6 November 2026 (Render environment-group UI issue and account handoff)

## Latest owner report
- Owner says they created a Render environment group named **THINK TANK**.
- On checking its linked services, the owner sees an empty/blank linked-services area and cannot find a link control or pathway. They report that the page only shows explanatory write-up and a blank box.
- Owner has run out of attachment capacity in the current account and intends to continue in another ChatGPT account to upload a screenshot.
- Do not tell the owner to delete/recreate the group or repeatedly ask them to navigate blindly. Wait for the screenshot in the continuation account and inspect the exact page before giving UI instructions.
- The owner says SMTP variables have been added, but do not claim their presence, values, sender verification or successful delivery are independently confirmed.

## Verified Render documentation for linking an Environment Group
Official Render documentation: https://render.com/docs/configure-environment-variables
The documented route is: open the target **service** (not the Environment Group details page) → **Environment** in the left pane → find **Linked Environment Groups** → choose the group from the dropdown → click **Link**. Render says linking triggers a deploy to incorporate the group values.
If the service's Environment page does not show that section/dropdown, do not guess. Inspect the screenshot and establish whether the owner is in the group details page, a project/environment-scoped page, or the service page. Check whether group/service are in different workspaces or project-environment scopes. The official docs state a group scoped to a project environment cannot be linked to a service outside that environment; unscoped groups can be linked to services in the same team.
Important: a service-level variable overrides a same-named variable from a linked group. Avoid duplicate keys across multiple groups.
Do not cause a deployment or configuration mutation without explaining the effect and respecting the existing approval gates. Render's current dashboard save/link behavior may trigger deployment; this service has auto-deploy disabled, but verify current state.

## Immediate continuation instructions for the next AI account
1. Read this entire file first and continue from this checkpoint; do not restart the project or repeat completed work.
2. Owner will provide a screenshot showing the Render page where the THINK TANK group has no visible linked-service control. Identify the exact page from visible headings/navigation, then provide precise next clicks only if supported by the screenshot and current Render docs.
3. If UI remains ambiguous, inspect the Render account/service/group through available Render app tools. Do not claim access to group details or secret values unless the tool actually returns them. Never ask owner to reveal SMTP key/password.
4. Resolve the group/service linkage only if it is appropriate and owner has approved the resulting deployment. If the dashboard truly offers no linking option, document the evidence and use a supported Render workflow; do not invent a hidden button or API.
5. Once linked/configured, verify controlled SMTP delivery to an owner-controlled test mailbox, first ensuring Brevo sender verification and correct SMTP login/key. Registration must remain disabled except for a tightly controlled, owner-approved staging test; disable it immediately afterward.
6. Continue the engineering work autonomously after this issue: verify current repo head, PR #1, CI, Render deployment SHA and staging health; then progress through the unfinished release gates in the main prompt. Keep PR #1 draft/open/unmerged and keep main untouched.
7. Update this master prompt at every meaningful milestone with exact verified links, commit SHA, test results, provider state, remaining owner-only gates and next action. Never include secrets.

## Transfer message for a fresh ChatGPT account
Paste the following instruction, then attach the Render screenshot:
“Continue my Think Tank platform project from this master continuation file. Read it fully and inspect the current GitHub/Render/Neon state before acting. I am attaching a screenshot of the Render Environment Group named THINK TANK because the Linked Services area appears blank and I cannot find a link option. Diagnose the exact screen and guide me through only the necessary next step. Then continue the build autonomously from the recorded checkpoint, preserving all repository and deployment safety rules. Do not restart, do not ask me to repeat recorded details, and do not expose or request secrets.”


---

# Continuation checkpoint — 6 November 2026 (Render environment-group diagnosis and live provider reconciliation)

## Screenshot diagnosis
- The owner supplied a Render mobile-dashboard screenshot.
- The screenshot is the THINK TANK Environment Group details page, not the learnwise-staging-api service's Environment page.
- The group page shows an empty Linked Services panel and a visible Save only control. This is expected when a group has not yet been linked; the absence of a link button on the group page is not evidence of a broken group.
- Current official Render route: open the target service → Environment → Linked Environment Groups → choose the group → Link. Render documentation: https://render.com/docs/configure-environment-variables
- The owner should first select Save only on the current group editor, then open https://dashboard.render.com/web/srv-dbkqcmt9fdbs73c2kdpg and inspect the service's Environment page.
- Do not click Link yet. Linking triggers a deploy. Before linking, compare key names and confirm the staging DATABASE_URL target/role privately. The screenshot shows DATABASE_URL, AWS storage variables, SMTP variables, payment and registration flags in the group; SMTP variables were also previously reported as being set directly on the service. Service-level values override same-named group values. Render does not guarantee precedence between multiple linked groups.
- Owner must not reveal values or secrets in screenshots. Ask for a screenshot of the service Environment page with all values masked if UI guidance is still needed.
- The connected Render tools available in this session do not expose environment-group list/detail/link operations or environment-variable readback. Do not claim to have independently inspected group values, scope, service links, or secret contents.

## Verified GitHub state — 6 November 2026
- Repository: https://github.com/JephterAce/Year-1-Tutorial
- Active branch: secondary-school-platform-foundation
- PR #1 remains open, draft, mergeable and unmerged: https://github.com/JephterAce/Year-1-Tutorial/pull/1
- Branch head at this checkpoint: d35bebf6faa7690fd0412445d4fff5017126b70e.
- CI run 42270003444 completed successfully on that exact head: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42270003444
- Both jobs passed: api-tests and container-build. The API job includes unit/security tests, frontend/admin JavaScript syntax checks, disposable PostgreSQL migration replay, schema integration, and assessment/payment database E2E tests. Payment provider behavior in CI is mocked; this is not a real Paystack sandbox test or live staging browser acceptance.
- Relative to the current Render live commit 26d83096b0fd89812b5a1c749798293a2ad1e2b1, the development branch is 4 commits ahead. The four commits include the staging owner-bootstrap workflow and this handover checkpoint. No code deployment was performed during this session.
- Keep PR #1 draft/open/unmerged and keep main untouched.

## Verified Render state — 6 November 2026
- Workspace: Emmanuel's workspace (the only workspace returned by the connected Render account listing).
- Service: learnwise-staging-api, ID srv-dbkqcmt9fdbs73c2kdpg.
- URL: https://learnwise-staging-api.onrender.com
- Dashboard: https://dashboard.render.com/web/srv-dbkqcmt9fdbs73c2kdpg
- Connected branch: secondary-school-platform-foundation; Docker context secondary-school-platform; Dockerfile secondary-school-platform/backend/Dockerfile.
- Region Frankfurt, Free plan, one instance.
- Auto-deploy remains off (autoDeployTrigger=off).
- Latest live deployment: dep-dbmf0h8ae00c73fcf1sg, commit 26d83096b0fd89812b5a1c749798293a2ad1e2b1, status live.
- Health-check path remains blank.
- HTTP /health and manual browser acceptance were not verified in this session. The web fetch could not access the endpoint and the container had no DNS/network access; this is an access limitation, not evidence that the endpoint is down.
- SMTP environment values, sender verification and real delivery remain unverified. Never request or expose SMTP secrets.

## Verified Neon staging state — 6 November 2026
- Project: learnwise, ID spring-cloud-84267029.
- Staging branch: think-tank-staging, ID br-still-cherry-baz7g5hk; non-default, non-primary, ready.
- Database: learnwise, PostgreSQL 16.
- Read-only aggregate query returned: 6 subjects, 0 topics, 0 students, 1 administrator, 1 audit event, 13 migration records.
- The single audit event is admin.bootstrap.created at 2026-11-06T09:19:37.798Z.
- The single admin record is an active owner role. This verifies that the one-time owner bootstrap occurred in the staging database; admin login, CSRF behavior and capability-gated admin operations have not yet been browser-tested.
- Private bucket learnwise-private-audio exists with access level private; object listing returned zero objects. Neon storage is enabled. No object writes/deletes or migrations were performed in this session.
- Render's actual DATABASE_URL and S3 secret values are not readable through the connected Render integration. A trusted operator must privately confirm that Render targets this Neon staging branch/database and uses the least-privilege learnwise_app role.

## Outstanding gates and next work
1. Owner action: tap Save only on the current THINK TANK group page, then open the staging service's Environment page and provide a masked screenshot showing the Linked Environment Groups section and relevant variable names only. Do not click Link yet.
2. Before linking, reconcile duplicate keys and privately verify DATABASE_URL is the staging branch with learnwise_app; confirm the group is not scoped to a different project environment. Linking requires explicit approval because Render triggers a deployment.
3. Run the manual workflow .github/workflows/think-tank-staging-browser.yml from GitHub Actions → Think Tank staging browser acceptance → Run workflow. The connected GitHub integration does not expose workflow dispatch.
4. Test the newly bootstrapped owner login and protected admin routes using the owner's private password; never request the password in chat.
5. Complete real Brevo sender verification and controlled SMTP delivery tests; keep student registration disabled except for an explicitly approved, brief staging test.
6. Complete Paystack sandbox transactions/webhooks/retries/reconciliation; keep checkout and live payments disabled.
7. Complete private audio object-storage E2E; the bucket is still empty.
8. Obtain authorised NERDC curriculum source materials and reuse rights, map all 18 class/subject combinations, and obtain qualified teacher review.
9. Complete Nigerian DPIA, NDPA/legal, child/guardian consent and safeguarding approvals.
10. Complete full CMS/admin operations, student profile/export/deletion UAT, monitoring, backup/restore, accessibility and independent security review.
11. No production release. No main-branch change, PR merge, paid resource, production migration, live payment, or production deployment is authorised.

## Session outcome
- Completed: full master prompt read; screenshot identified; current GitHub/Render/Neon state reconciled; owner bootstrap independently verified in Neon; current exact-head CI verified green.
- Not completed: Environment Group linkage, HTTP/browser staging acceptance, SMTP delivery, Paystack sandbox, audio E2E, curriculum/legal/teacher gates, production readiness.
- Next checkpoint: resume after the owner saves the group and opens the staging service's Environment page. Continue without rebuilding completed foundations.


## Post-checkpoint reconciliation note — 6 November 2026
- The prior checkpoint was committed as a documentation-only change at branch head 53d5f36851fbdac3ec7c93bc21403593ce837eec. No application source, migration, deployment configuration or secret was changed by that commit.
- GitHub currently reports PR #1 as open, draft and unmerged, but its mergeable field is false. The reason is not established. Do not attempt a merge, rebase, branch sync or main update. The default main branch has two commits beyond the PR merge base; the only two files in those main-only commits have identical blob SHAs on main and the development branch. This confirms those two file contents match, but does not explain GitHub's mergeable=false status.
- CI run 42270003444 remains the latest verified full code-test run and passed on the immediately preceding code head d35bebf6faa7690fd0412445d4fff5017126b70e. No new workflow run was returned for the docs-only commit 53d5f36851fbdac3ec7c93bc21403593ce837eec. Treat the source-code CI evidence as green on d35; do not claim a new exact-head test on the documentation commit.
- Re-fetch the live PR head and CI before the next repository write. The next handover update itself will create a new documentation commit; obtain its resulting SHA from GitHub after the update.


---

# Continuation checkpoint — 6 November 2026 (Owner linked THINK TANK group; exact-head CI green)

## Render environment group action
- Owner reports selecting **Link only** for the existing Render environment group named **Think Tank** on service `learnwise-staging-api`.
- The Render service page showed the Link only option selected in the owner screenshot. The owner subsequently confirmed the action was completed.
- The connected Render app integration does not expose environment-group list/retrieve/link APIs, and the available service-detail response does not include linked environment group IDs. Therefore the linkage is **owner-reported, not independently API-verified**. Confirm in the dashboard that Think Tank appears under Linked Environment Groups before treating the link as verified.
- Render service API recheck: `autoDeploy=no`, `autoDeployTrigger=off`; latest deployment remains `dep-dbmf0h8ae00c73fcf1sg`, commit `26d83096b0fd89812b5a1c749798293a2ad1e2b1`, status `live`. No new deployment/build event appeared after the owner-reported Link only action.
- No deployment was triggered by the assistant. Do not assume the group is correctly configured simply because it was linked. Service-level variables override matching group variables; avoid collisions and verify that the effective `DATABASE_URL` privately targets the Neon staging branch/database and least-privilege `learnwise_app` role before any deployment. Never reveal secret values in chat or handover.
- The Render integration currently does not expose environment-group contents or secret readback. Do not attempt to infer the actual values from masked screenshots.

## Latest GitHub and CI verification
- Branch head at start of this checkpoint: `072790914bf656d1c175a33d9eedcac2fb23c98c`.
- PR #1 remains open, draft and unmerged. GitHub currently reports `mergeable=true` (this supersedes the previous checkpoint's transient `mergeable=false` observation). Do not merge.
- Two current-head workflow runs completed successfully:
  - Pull request run `42271262201`: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42271262201
  - Push run `42271251648`: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42271251648
- Both runs executed `api-tests` and `container-build`, both successful. API job steps passed: unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL migration rehearsal, schema integration, assessment/payment database E2E. Container build completed without publishing.
- This is a verified green CI result on the exact branch head above. Provider integrations in CI are not a substitute for real SMTP, Paystack sandbox, private object storage or live browser tests.

## Current Render deployment / live test status
- Service: `learnwise-staging-api`, ID `srv-dbkqcmt9fdbs73c2kdpg`.
- Auto-deploy remains disabled.
- Latest deployment remains `dep-dbmf0h8ae00c73fcf1sg` on commit `26d83096b0fd89812b5a1c749798293a2ad1e2b1`; it has not been advanced to the current branch.
- The public `/health` URL could not be fetched by the web retrieval client; this is an access/tool limitation and does not prove the service is down.
- Do not set Render's health-check path or deploy current branch until the manual browser acceptance workflow and private staging environment verification are complete.

## Next required owner action
- In GitHub Actions, manually run **Think Tank staging browser acceptance** from `.github/workflows/think-tank-staging-browser.yml`, using the default staging URL. The workflow dispatch is not exposed by the connected GitHub integration. Review its full result and uploaded Playwright report/traces before proceeding.
- Separately, verify in Render that Think Tank appears under Linked Environment Groups and privately confirm the effective staging database and storage configuration. If the group does not appear, stop and report the exact dashboard state; do not try to link repeatedly.
- Deployment approval is still required before advancing the staging service to the newer branch. No production deployment or main-branch change is authorised.

## Neon recheck
- Staging branch remains `think-tank-staging`.
- Read-only counts remain: 1 administrator, 0 students, 1 audit event, 13 migration records.
- No database writes, migrations, object writes/deletes, or credential changes were performed in this checkpoint.

## Session outcome
- Completed: owner reports Link only action; Render deployment state rechecked; exact-head GitHub CI verified green; PR state rechecked; Neon aggregate counts rechecked.
- Not independently verified: environment-group linkage in Render UI, effective variable values, service-to-Neon connection, live health endpoint, authenticated browser acceptance.
- Not performed: deploy, migration, payment activation, PR merge, main update, production change.


## Follow-on verification — 6 November 2026
- GitHub Actions produced two successful exact-head CI runs on `072790914bf656d1c175a33d9eedcac2fb23c98c`: PR run `42271262201` and push run `42271251648`. Both `api-tests` and `container-build` passed. The API job completed unit/security tests, JS syntax checks, disposable PostgreSQL migration rehearsal, schema integration and assessment/payment database E2E.
- The staging browser-acceptance workflow was inspected. It is a manual `workflow_dispatch` and performs read-only HTTP/browser checks: health, public pages, registration/login/recovery form controls without submitting data, anonymous API authorization, private audio denial, and anonymous admin redirects. It does not create student/admin records or submit real payments. The connected GitHub integration has no workflow-dispatch action; owner/operator must start it in the GitHub Actions UI. Direct workflow URL: https://github.com/JephterAce/Year-1-Tutorial/actions/workflows/think-tank-staging-browser.yml
- The current PR API observation subsequently returned `mergeable=false` again (PR remains open, draft and unmerged). GitHub's mergeability field has varied between reads; cause is unknown. Do not merge, rebase, sync main, or take action on this field without a separate review.
- A latest deployment-list recheck still shows only the existing live deployment `dep-dbmf0h8ae00c73fcf1sg` on commit `26d83096b0fd89812b5a1c749798293a2ad1e2b1`. No new Render build/deployment occurred after the owner-reported Link only action. Auto-deploy remains off.
- The owner-reported group link remains not independently visible through the connected Render service API. Verify visually that `Think Tank` appears in Linked Environment Groups.


## Browser acceptance workflow dispatch blocker — 6 November 2026
- Owner supplied a screenshot of GitHub Actions → All workflows. The left workflow list contains only "Secondary-school platform checks" and "Staging owner admin bootstrap (one-time)"; "Think Tank staging browser acceptance" is absent.
- Verified the exact workflow file `.github/workflows/think-tank-staging-browser.yml` exists on `secondary-school-platform-foundation` (blob `8fe95c383024d621e9f502549391bfd2de2557c6`) and declares `workflow_dispatch`.
- Verified the same path does **not** exist on the repository default branch `main` (GitHub contents API returned 404).
- Root cause: GitHub only makes a `workflow_dispatch` workflow manually runnable when its workflow file exists on the default branch. The workflow cannot be launched from the Actions UI while it exists only on the development branch.
- Do not copy/add this workflow to `main` without the owner's explicit approval; owner has explicitly prohibited main modifications.
- Safe alternative under consideration: execute the existing Playwright browser-acceptance suite from a Codespaces terminal checked out on `secondary-school-platform-foundation`, targeting the existing staging URL. This is a read-only browser test suite, but inspect package/test files and confirm the staging service/database environment first. Do not deploy, change main, or submit forms/transactions.
- Owner was not at fault; there is no missing Run workflow button to find on the current page.


## Staging deployment — 6 November 2026 (Render deployment succeeded)
- Owner explicitly confirmed the Render workspace **Emmanuel's workspace** (workspace ID `tea-da2svh0ae00c73cs4qq0`) for this Think Tank staging operation.
- Manually triggered Render deployment for service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) using the service's configured development branch `secondary-school-platform-foundation`. Auto-deploy remains disabled.
- Deployment ID: `dep-dbn2dcrl550s73f9ahag`.
- Deployed commit: `0f343fff800b619fdaff76f5ee97225ec6c3dbdf` — `docs(think-tank): record browser workflow dispatch blocker`.
- Render build completed successfully; Docker image export/push succeeded. Gunicorn 23.0.0 started, bound to `0.0.0.0:8000`, and booted workers. Render logged **Your service is live** at 2026-11-06T19:13:13Z. Render deploy API subsequently returned status `live` with finishedAt `2026-11-06T19:13:13.356186Z`.
- Staging URL: https://learnwise-staging-api.onrender.com
- Dockerfile includes a container health probe for `/health`. Source inspection confirms Flask implements `GET /health`: it returns demo-mode OK if `DATABASE_URL` is absent, checks `database_ready()` when `DATABASE_URL` is present, and returns HTTP 503 if the database is unavailable. This route has **not yet been externally exercised**; the web retrieval client could not access the endpoint, and Render HTTP request metrics returned no samples in the inspected interval. Do not claim database connectivity or application readiness solely from Render's generic live status.
- No database migrations, database writes, admin bootstrap, payment transactions, audio uploads, production changes, PR merge, or main-branch changes were performed during this deployment.
- Owner stated that the required environment variables are already captured in the Render environment configuration. The Render service API does not expose the effective secret values or Environment Group linkage, so those remain owner-reported and are not independently verified. No secret values were read or disclosed.
- Browser acceptance test source was inspected: Playwright suite has eight read-only checks covering health, student pages, account form controls without submission, anonymous student/private API denial, assessment/audio denial, admin identity denial, admin redirects, and admin login form separation. It deliberately does not create users or submit transactions. The GitHub Actions workflow remains undispatchable through the available connector and absent from `main` (which must remain untouched). The suite has **not** been run against staging yet.

## Next staging verification steps
1. Independently request `https://learnwise-staging-api.onrender.com/health` and confirm JSON `status: ok` with `mode: database` (not demo). If it reports 503/degraded, inspect the staging database connection and effective Render `DATABASE_URL` privately; do not paste secrets into chat.
2. Run the existing Playwright suite from Codespaces on `secondary-school-platform-foundation` with base URL `https://learnwise-staging-api.onrender.com`. The suite is read-only; do not submit registration, payment, or other state-changing actions.
3. Verify student/admin pages and anonymous authorization behaviour. Test authenticated admin login only through the owner-controlled browser session; never request or print the password.
4. Verify SMTP delivery and Paystack sandbox separately using test credentials; no live payment. Private audio storage remains unpopulated and private.
5. Keep production release gated on privacy/safeguarding/legal/teacher/curriculum, backup/restore, security and operational approvals. No production release is authorised.

## Staging health and database connectivity verified — 6 November 2026
- Owner opened `https://learnwise-staging-api.onrender.com/health` and supplied the exact JSON response:
  ```json
  {"mode":"database","service":"secondary-school-api","status":"ok"}
  ```
- This is direct external HTTP evidence that the deployed Flask health route returned HTTP success with `status=ok` and `mode=database`. The route's database-mode readiness check calls `database_ready()`; therefore the app successfully reached its configured PostgreSQL database at the time of the request.
- This confirms runtime database connectivity for the staging service, not the correctness of every schema/query, all application routes, or production readiness. The effective secret values and precise database target remain unreadable through the connected Render integration; the response confirms successful DB readiness but does not independently identify the Neon branch/role.
- Render deployment remains the already verified live deployment `dep-dbn2dcrl550s73f9ahag` on application commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`. No redeploy, migration, database write, payment, storage upload, or production change was performed for this health check.
- Inspected the exact browser acceptance suite on `secondary-school-platform-foundation`: `secondary-school-platform/browser-acceptance/staging.spec.js`, package script `npm test`, Playwright 1.56.1, Chromium. It contains eight read-only tests for health, student-facing pages, account form controls without submission, anonymous student/private API authorization, assessment/audio denial, administrator identity denial, admin redirects, and separation of the admin login form. The workflow is `.github/workflows/think-tank-staging-browser.yml`; it installs dependencies and Chromium, runs the suite against the supplied staging base URL, and uploads report/traces. It does not submit registration, payment or other state-changing actions.
- The browser suite has not yet been executed. The connected GitHub integration still cannot dispatch the workflow, and it remains absent from `main`; do not modify `main` to expose it. The remaining safe route is to run the existing suite from a Codespaces terminal on the development branch, using the staging URL. A user/operator terminal action is required because no Codespaces execution tool is exposed here.
- Exact command from the repository root in Codespaces:
  ```bash
  cd secondary-school-platform/browser-acceptance && npm install && npx playwright install chromium && STAGING_BASE_URL=https://learnwise-staging-api.onrender.com npm test
  ```
  This runs only the existing read-only browser checks. Do not add credentials, submit forms, or enable registration.
- Remaining gates include authenticated owner-admin browser testing (owner-controlled session only), controlled SMTP delivery, Paystack sandbox, private audio E2E, curriculum provenance/teacher review, privacy/safeguarding/legal review, and backup/restore/operational readiness. No production release is authorised.


## Staging browser acceptance — 6 November 2026 (owner reports all checks passed)

- Owner ran the existing Playwright suite from the Codespaces terminal on the development branch, targeting `https://learnwise-staging-api.onrender.com`, and reported **all 8 tests passed**.
- Test suite: `secondary-school-platform/browser-acceptance/staging.spec.js`; command used:
  ```bash
  cd secondary-school-platform/browser-acceptance && npm install && npx playwright install chromium && STAGING_BASE_URL=https://learnwise-staging-api.onrender.com npm test
  ```
- The eight checks cover: staging health response; student-facing pages; account registration/login/recovery controls without submitting forms; anonymous student/private API authorization; anonymous assessment/audio access denial; anonymous admin identity denial; admin route redirects/noindex; and admin login form separation.
- Evidence classification: **owner-reported execution result** (owner confirmed “All 8 passed” in chat; the terminal output, Playwright HTML report and trace files were not shared or independently retrieved). Do not represent this as a GitHub Actions run or attach a workflow-run ID.
- The suite is read-only by design. No account creation, form submission, payment, audio upload, or database mutation was performed by this test run.
- Render recheck after test: service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) remains on `secondary-school-platform-foundation`, auto-deploy off, not suspended. Latest deployment `dep-dbn2dcrl550s73f9ahag` remains `live`, deployed application commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`. The previous deployment was deactivated as expected. No redeploy was triggered after the browser suite.
- Neon staging recheck (project `spring-cloud-84267029`, branch `br-still-cherry-baz7g5hk`, database `learnwise`, read-only `learnwise_app` query): 6 subjects, 0 topics, 0 students, 1 administrator, 1 audit event, 13 recorded migrations. The private `learnwise-private-audio` bucket exists and contains zero objects. The database contains the expected core tables for students, sessions, subjects/topics, lessons/progress, assessments/attempts/answers/integrity, payment transactions/webhooks/outbox, identity tokens, consent and data exports.
- The staging `/health` endpoint was previously externally confirmed by the owner to return `{"mode":"database","service":"secondary-school-api","status":"ok"}`; this is evidence of runtime PostgreSQL connectivity at that time, not proof that every feature or schema path is correct.
- No application source, schema, secret, deployment setting, production environment, `main` branch, or PR state was changed for this milestone. PR #1 remains protected: keep it open, draft and unmerged.

## Next engineering sequence after public browser acceptance

1. Inspect and complete owner-controlled authenticated admin login and authorization UAT. Owner enters credentials only in their browser; never request or transmit the password in chat. Verify admin dashboard, operations/reviews pages, CSRF, role/capability restrictions and audit events. Do not bootstrap another admin.
2. Verify Brevo sender identity and perform controlled SMTP delivery to an owner-controlled mailbox. SMTP variable presence/effective values and sender verification remain unverified through the available Render connector. Keep student registration disabled unless a separate short staging test is explicitly approved; do not expose or request SMTP secrets.
3. Complete Paystack sandbox checkout, signed webhook verification, idempotency, retries and reconciliation using test credentials only. Live payments remain disabled.
4. Complete private audio upload/playback authorization and signed URL/streaming E2E in staging. Bucket is private and currently empty; no upload or object mutation is authorized by the prior browser suite.
5. Audit student lifecycle, assessment attempt integrity/grading, admin content-management and support/reporting workflows. Add targeted tests and fix gaps on the development branch only; deploy reviewed staging changes with explicit staging authorization and verify each deployment.
6. Obtain authoritative NERDC source materials and reuse rights, map all 18 class/subject combinations, and secure qualified Nigerian subject-teacher review before publishing curriculum content.
7. Complete NDPA/privacy impact assessment, child/guardian consent, safeguarding, legal review, accessibility, independent security review, monitoring, backup/restore and rollback evidence.
8. Prepare a release-readiness report. Production remains blocked until all applicable gates are evidenced and the owner separately authorizes production deployment.

Owner-only actions should be batched and requested only when a genuine account, credential, sender verification, provider transaction, legal/teacher approval, spend or deployment approval is required. Continue all safe code review, tests and documentation autonomously in the meantime. Never claim the platform is production-ready based only on the eight anonymous/public browser checks.


## Admin portal source review — 6 November 2026
- Source inspection confirms `/admin/login`, `/admin`, `/admin/operations` and `/admin/reviews` are served by the staging Flask application. The protected workspace/operations/review pages redirect anonymous visitors to the dedicated `/admin/login` page; successful owner authentication is required to proceed.
- The admin login uses the separate `learnwise_admin_session` HttpOnly, SameSite=Strict cookie and a CSRF cookie. Admin authentication uses a database-backed eight-hour session and a six-attempt/15-minute rate limit keyed with `AUTH_RATE_LIMIT_PEPPER`. Admin provisioning is deliberately offline-only; do not create another administrator or rerun bootstrap.
- The operations page calls real protected APIs for platform overview, students, payments, curriculum sources and audio assets. The review page calls the protected assessment issue queue and review endpoint. Backend authorization uses explicit role capabilities; state-changing review/upload operations require CSRF validation. The audio upload endpoint validates MIME/signature/size and stores objects in private storage, but has not been exercised end-to-end.
- Owner-only verification still required: use the owner's own browser to sign in at `https://learnwise-staging-api.onrender.com/admin/login`, then confirm the dashboard, operations page and review page load without errors. Do not send credentials, cookies, CSRF tokens or one-time links through chat. If sign-in fails, report only the visible error message; do not repeatedly retry because the endpoint is rate-limited.
- The read-only database recheck after the browser suite remains 6 subjects, 0 topics, 0 students, 1 administrator, 1 audit event and 13 migrations. Thus the staging portal currently has no student or topic content to display; this is an empty-content state, not a failed database connection.
- SMTP, Paystack sandbox, private audio upload/playback, full authenticated admin UAT, content/curriculum rights and teacher review, privacy/safeguarding/legal approval, accessibility/security review, monitoring, backup/restore and production release remain open gates. No production deployment is authorised.

## Authenticated admin staging UAT — 2026-11-06
- Owner confirmed successful sign-in to the staging administrator portal.
- Owner then confirmed that both authenticated pages loaded successfully:
  - `/admin/operations`: overview and sections for students, payments, curriculum sources, and audio assets rendered.
  - `/admin/reviews`: assessment review queue rendered.
- Evidence classification: owner-reported visual/browser verification. No screenshots, session cookies, passwords, or tokens were requested or received.
- No administrative mutations were performed: no student creation, payment action, content edits, review decisions, audio uploads, or settings changes.
- This confirms authenticated page access and dashboard rendering only. It does not yet verify individual write operations, CSRF enforcement, fine-grained role restrictions, email delivery, Paystack sandbox, or private audio end-to-end.
- Existing staging safety boundaries remain unchanged: no production deployment, no main-branch changes, no PR merge, no destructive DB/object-storage actions, and no live payments.
- Next verification: complete a read-only review of the authenticated admin UI/API permissions and audit behavior; then batch any owner-only provider checks (sender verification, sandbox payment, and private audio workflow) before requesting additional manual steps.
