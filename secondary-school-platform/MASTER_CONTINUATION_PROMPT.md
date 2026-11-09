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

## Admin authorization and audit source review — 2026-11-06
- Reviewed `backend/admin_policy.py`, `backend/admin_auth.py`, `backend/admin_data.py`, and `backend/admin_assessment_reviews.py` on `secondary-school-platform-foundation`.
- Authorization is default-deny: unknown/inactive/malformed principals and unknown capabilities are rejected. Roles are mapped to explicit capability sets; owner has all declared capabilities, while editor, reviewer, support, and analyst have narrower sets.
- Admin sessions are database-backed, hashed at rest, expire after eight hours, and are checked against active admin status. Login uses a generic credential error and a six-attempt/15-minute rate limit. CSRF validation is required for review decisions and audio upload/review mutations.
- Operations API endpoints gate student, payment, curriculum, and audio data by capability. Read views write audit events with returned-record counts. Assessment review decisions update the report and insert the corresponding audit event in the same database transaction.
- Audio upload/review endpoints are state-changing and require CSRF plus the relevant capability. They were not exercised; no upload or review mutation was attempted.
- Source review is not a substitute for runtime negative tests across each role. Only the owner account is currently provisioned, so editor/reviewer/support/analyst role behavior remains code-reviewed, not live-verified.
- Owner's successful dashboard rendering confirms the authenticated UI path and the relevant read views returned sufficiently to render. It does not establish all role boundaries, CSRF rejection behavior, or mutation/audit behavior end-to-end.
- No application code was changed during this review. The only change is this handover documentation update.

## Email and Paystack implementation source review — 2026-11-06
- Reviewed `identity_email.py`, `payment_orders.py`, `payments.py`, `paystack_verification.py`, `paystack_webhooks.py`, `payment_notifications.py`, `payment_outbox.py`, and the payment fulfilment functions in `database.py`.
- Identity email delivery requires configured SMTP host/username/password, validates sender and recipient syntax, uses STARTTLS for non-465 SMTP ports or implicit TLS on 465, and refuses a non-HTTPS public application URL. No SMTP message was sent and effective Render settings/sender verification remain unverified.
- Checkout initialization takes the amount from the published topic record (not a client-supplied amount), requires an active verified student, uses NGN, and accepts only HTTPS Paystack checkout URLs on `checkout.paystack.com`.
- Webhook handling verifies the HMAC-SHA512 signature over the raw body, accepts only a successful NGN `charge.success` event, then independently calls Paystack's server-side transaction verification and compares reference, amount, status, and currency before fulfilment.
- Fulfilment locks the payment row, validates it against the verified transaction, updates payment status, inserts entitlement, records a webhook event, and queues an owner alert in a database transaction. Unique/deduplication constraints are used for webhook events, entitlements, and owner-alert outbox entries. The outbox worker uses `FOR UPDATE SKIP LOCKED`, bounded retries, and dead-letter handling.
- Existing unit-test files cover Paystack initialization, webhook signatures/event validation, and server-side transaction verification. Source files were inspected; these tests have not been independently executed in this review and no real Paystack transaction was attempted.
- Important remaining runtime gates: verify staging uses Paystack test credentials only; complete a controlled sandbox checkout/webhook/idempotency/reconciliation test; verify SMTP sender identity and a test delivery to the owner-controlled mailbox; and confirm a deployed/scheduled worker actually drains the payment notification outbox. No SMTP send, payment, database write, or worker trigger was performed.
- No application code was changed during this source review. The only change is this handover documentation update.


---

# Continuation checkpoint — 6 November 2026 (full-product build authorization and student/AI audit)

## Owner direction
The owner confirmed that the intended product is the complete AI-powered secondary-school learning ecosystem: AI teaching/explanations, structured lessons, student Q&A, educational podcasts/audio, practice and timed assessments, marking/feedback, progress tracking, paid resources and personalized recommendations. The owner authorized continuing development toward that full scope. This is not authorization for production deployment, live payments, destructive database operations, public student onboarding, or spending.

## Repository baseline verified for this checkpoint
- Repository: `JephterAce/Year-1-Tutorial`
- Development branch: `secondary-school-platform-foundation`
- Branch head at audit start: `7f10947ec85fd183b5b7630efe448afd8d731288`
- PR #1 remains open/draft/unmerged per the current handover; recheck before future changes.
- Render staging currently runs older app commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`; Render auto-deploy remains off. Documentation-only commits are not deployed automatically.
- No application source, environment configuration, database, production branch, or staging deployment was changed during this audit.

## Student and learning experience audit (source inspection)
- Existing frontend files: `frontend/index.html`, `account.html`, `lesson.html`, and `assessment.html`.
- Existing account routes include registration (feature-flag gated), email verification, login/logout, current-session lookup and password reset. Tests in `test_identity_routes.py` mock identity/email services; they do not establish real SMTP delivery or full student lifecycle against the managed staging database.
- Student homepage has a substantial visual dashboard/catalogue/profile experience, but source contains illustrative/static dashboard counters and should not be treated as proof that all dashboard widgets are populated from live student records.
- Lesson page fetches a topic, checks entitlement, offers checkout and requests private audio access. No approved topic rows or audio objects were present in the last verified staging DB/storage snapshot; lesson/audio journey is therefore not end-to-end proven.
- Assessment page contains catalogue, briefing, answer-save, timer, submit/result and report/appeal UI. Backend assessment services and unit/contract tests exist, but the full authenticated student journey against real staging content has not been run.
- Current staging browser suite covers eight anonymous/unauthenticated access and page-shell checks; it does not cover registration, email, authenticated student dashboard, paid entitlement, live checkout, audio playback or a complete assessment.

## AI teaching and content audit
- Recursive development-branch tree inspection found no AI tutor/provider adapter, AI chat route, prompt orchestration service, model configuration module, or AI-specific tests.
- Existing audio delivery/storage infrastructure and one General Mathematics algebraic-expressions two-presenter script draft exist. That script explicitly remains unassigned to class/term and unreviewed; it is not a published curriculum asset.
- No podcast generation/transcription/voice-production pipeline was found in the backend tree. The existing outbox worker is for payment alert email only, and backend README says it is not scheduled or monitored.
- Last verified Neon staging snapshot had six subject rows but zero topics, zero students and one owner admin. Thus the six subjects do not yet constitute a populated SS1–SS3 curriculum.
- No AI API/provider credential or external AI provider integration was inspected or configured. Do not ask the owner to paste credentials into chat.

## Immediate engineering priorities
1. Implement a secure, provider-abstracted AI tutor backend with authenticated student ownership, request limits, prompt-injection boundaries, age-appropriate tutoring policy, provider timeouts, cost/token limits, and tests using mocked provider responses. Keep AI output clearly labelled as assistance and do not let it change grades, entitlements or curriculum publication state.
2. Integrate the student frontend with real session/catalogue/profile/progress APIs and remove misleading hardcoded progress values for signed-out/empty accounts. Add explicit loading, empty, error and locked states.
3. Add a complete authenticated student browser journey using synthetic test data in an isolated test environment; do not create test accounts or mutate managed staging without owner approval.
4. Implement the learning-content and podcast production workflow as a reviewed, versioned process. Keep scripts/audio unpublished until source rights, qualified subject review and technical QA are recorded.
5. Schedule and monitor the payment notification outbox only after staging SMTP is verified; this worker must not be confused with AI/audio generation workers.

## Tooling constraint and evidence boundary
The available GitHub integration supports repository file reads/writes but exposes no Codespaces terminal or arbitrary repository shell execution in this session. Consequently this checkpoint records source inspection only; no Python tests, lint, browser tests, or AI-provider integration tests were executed here. Use Codespaces/CI for executable verification before treating any implementation as complete.

## Owner-only gates still outstanding
- Confirm staging provider configuration privately (AI provider, SMTP, Paystack sandbox); never disclose values in chat.
- Complete real controlled SMTP and Paystack sandbox tests, with separate approvals for any operation that creates test data or transactions.
- Obtain official curriculum source materials and reuse rights, plus qualified Nigerian teacher review.
- Complete privacy, NDPA, child/guardian consent, safeguarding, independent security, accessibility and recovery reviews.
- Keep production deployment and public student onboarding blocked until explicit separate authorization and evidence-backed release approval.


---

# Continuation checkpoint — 6 November 2026 (AI tutor foundation implementation)

## Development changes committed
- Added `backend/ai_tutor.py`: provider-neutral OpenAI-compatible chat-completions adapter; bounded learner question/context and answer size; class-level-specific teaching prompt; HTTPS endpoint validation; explicit host allow-list; redirects blocked; 20-second provider timeout; 600-token output cap; provider errors sanitised.
- Added `POST /api/v1/tutor/answer` to `backend/app.py`. It requires a valid student session and CSRF token, uses class level from the authenticated session (not browser input), and returns only the tutor answer. It cannot change grades, payments, entitlements or curriculum state.
- AI feature flag is strict opt-in: `AI_TUTOR_ENABLED` must be explicitly true; otherwise the endpoint returns 503. The sample environment file keeps it false and documents provider variables without credentials.
- Added `backend/test_ai_tutor.py` covering prompt/input bounds, provider allow-list and credentials, bounded output, redirects, feature-disabled behaviour, authentication/CSRF gate and session-derived class level.
- Updated backend README with provider setup and rollout limitations.

## Commits
- AI tutor client: `a47d8fdd068f39d4e231332ef4c2a5bf3048d164`
- Protected API route: `ee71ea4ca19f4c05ac8e9bfe3cdca5c14942a25e`
- Initial tests: `73ab1379debce505abe9c7f004538d50832e6395`
- Protected route tests: `9ba7006cda18ec44d39d2cc47b3a229bb12d7e59`
- Strict opt-in gate: `88fd92ded4ab77c52fde18573f4151d507eadeda`
- Provider env example: `22e93d5f85b020d89ea27aaf061e86d41786c011`
- Backend documentation: `b64b6aca1e06183001a61fa0450d801748c8a484`
- Current development branch head at this checkpoint: `b64b6aca1e06183001a61fa0450d801748c8a484`

## Verification and rollout status
- GitHub Actions PR run `42295106769` for commit `9ba7006cda18ec44d39d2cc47b3a229bb12d7e59` completed successfully (API tests and container build). This was before the final strict-opt-in and documentation commits.
- CI for current head `b64b6aca1e06183001a61fa0450d801748c8a484` was queued/in progress when recorded; do not claim the latest commit has passed until the check suite reports success.
- No AI provider credentials were configured or read, no model request was made, and no learner data was sent to an external provider.
- No staging deployment was triggered; Render remains on its previously verified app commit. No database migration or write was performed.

## Explicit limitations before enabling AI tutor
- Durable per-student quotas, concurrent request throttling, daily/monthly spend limits and provider budget alerts are not implemented. The endpoint is not approved for learner use until these controls exist and are tested.
- No chat-history persistence, tutor frontend UI, streaming, content retrieval/grounding, teacher moderation workflow or independent answer-quality evaluation exists yet.
- AI answers must not be treated as verified curriculum, marking authority or a replacement for qualified teachers.
- Next engineering increment: implement database-backed usage quotas and cost controls with a new migration plus disposable-PostgreSQL tests; then integrate a learner-facing tutor interface and add authenticated browser acceptance. Keep the feature disabled until those controls and privacy review are complete.


---

# Continuation checkpoint — 6 November 2026 (approved full-product implementation, increment 2)

## Owner direction
The owner explicitly approved proceeding with all seven workstreams: database-backed AI usage/cost limits; student-facing AI tutor; live student dashboard/progress; lesson notes and interactive practice; podcast production/private audio; curriculum population across six subjects and SS1–SS3; and registration-to-results acceptance testing. Continue on `secondary-school-platform-foundation`. This does not authorize production deployment, public onboarding, live payments, or unreviewed managed-database mutations.

## Development branch
- Repository: `JephterAce/Year-1-Tutorial`
- Branch: `secondary-school-platform-foundation`
- Head at this checkpoint: `aa2ddb80ebf550136f41084615aed47c80f3d823`
- PR #1 remains draft/unmerged; `main` untouched.
- Render staging remains on previously verified app commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`; auto deploy is off. No new staging deployment was triggered.
- No managed Neon migration was applied. Migrations below exist only in the development branch until reviewed/rehearsed.

## Implemented application changes

### AI tutor and spend controls
- `backend/ai_tutor.py`: OpenAI-compatible provider adapter, class-level system instructions, bounded question/context/history, redirect blocking, HTTPS endpoint/host allow-list, 20-second timeout, 600-token output ceiling, sanitised provider errors.
- `POST /api/v1/tutor/answer`: requires an authenticated student and CSRF; class level comes from the student session, not the browser; accepts bounded multi-turn user/assistant history. AI output cannot change marks, entitlements, payments or curriculum state.
- `backend/ai_tutor_quota.py`: UTC per-student daily/monthly request limits and estimated-spend reservations, plus platform-wide daily/monthly spend caps. Uses PostgreSQL advisory transaction locks to serialize concurrent reservations. Reserves the full output-token ceiling and estimates input tokens from bounded prompt length. Failed calls remain counted to prevent retry abuse.
- Migration `014_ai_tutor_usage_limits.sql`: per-student daily usage table.
- Migration `017_ai_tutor_platform_budget.sql`: platform-wide daily usage table.
- Provider pricing is required in private environment variables as integer micro-USD per million input/output tokens; missing pricing fails closed. These are conservative estimates/reservations, not invoice reconciliation.
- `AI_TUTOR_ENABLED` remains false by default. No provider key, model tariff, external request or learner prompt has been configured/sent. Do not enable until private provider config, pricing verification, privacy review and QA pass.

### Student dashboard and lesson learning
- `GET /api/v1/student/dashboard` returns authenticated, database-backed student class, completed lessons, saved practice attempts, assessment attempts/passes/average score, class-specific published subject counts and recent completed lessons.
- `frontend/index.html` now loads real dashboard data, shows an AI tutor conversation interface and keeps tutor history in page memory only. Empty/signed-out state does not fabricate progress.
- Migration `015_reviewed_lesson_content_and_progress.sql` adds versioned lesson content, teacher-reviewed practice questions, topic completion progress and student practice-attempt history. Composite foreign keys bind progress and practice questions to the correct topic.
- `backend/lesson_content.py` enforces entitlement and publication checks, returns no answer keys to students, grades practice server-side, persists attempts, and records explicit lesson completion.
- Student routes:
  - `GET /api/v1/topics/<topic_id>/lesson-content`
  - `POST /api/v1/topics/<topic_id>/practice/<question_id>`
  - `POST /api/v1/topics/<topic_id>/progress/complete`
- `frontend/lesson.html` renders reviewed notes, worked examples, key terms and interactive practice, and can mark a lesson complete.
- Admin authoring/review routes in `backend/admin_data.py` allow curriculum editors to save draft content and practice questions; publishing-capable admins record the qualified teacher reviewer name before approval. Topic publication remains a separate evidence-gated operation.
- Admin UI `admin/index.html` now has source capture, topic draft, lesson draft/review and publication controls.

### Podcast production and private delivery
- Migration `016_podcast_script_workflow.sql` creates versioned podcast script records linked to the matching topic and lesson version.
- `backend/podcast_production.py` generates an original two-presenter script draft from approved lesson notes only; it does not invent lesson facts.
- Admin routes generate/list scripts, attach a pending private podcast audio asset and approve/reject the script. Script approval requires the linked audio asset to have passed its separate review.
- Admin UI includes script generation, private audio upload, attachment and review controls.
- Existing private audio storage and entitlement-checked streaming remain the student delivery path.
- This is a controlled script/record/upload/review pipeline, not an automatic TTS service. No voice provider was configured, and no audio file was generated or uploaded during this increment.

### Curriculum research and draft content
- `CURRICULUM_SOURCE_REGISTER.csv` records all 18 class/subject combinations (six subjects x SS1–SS3), their official source entry points and current capture status.
- `CURRICULUM_POPULATION_PLAN.md` records evidence, cohort transition and publication rules.
- Captured official October 2025 NERDC PDFs:
  - English Language SSS1: `https://lmis.nerdcportals.com.ng/sss_1/necurrdc/1.pdf`; 40 topic headings indexed in `content/curriculum-drafts/english-language/SS1_TOPIC_MAP.md`.
  - Biology SSS1: `https://lmis.nerdcportals.com.ng/sss_1/necurrdc/6.pdf`; 20 topic headings indexed in `content/curriculum-drafts/biology/SS1_TOPIC_MAP.md`.
- Original draft lesson packs created (not imported/published):
  - `content/curriculum-drafts/english-language/SS1/debate.lesson.json`
  - `content/curriculum-drafts/biology/SS1/laboratory-safety-rules.lesson.json`
- SSS2 official subject viewer links were found for English Language, General Mathematics, Biology, Chemistry and Physics, but their PDF text could not be extracted in this audit; Further Mathematics link needs repair. SSS3 class-specific subject documents remain outstanding. The register marks these honestly as viewer-link-only or pending.
- Do not infer term placement from topic order. Confirm cohort applicability and term mapping; get source/rights review and qualified subject-teacher approval before publication. No topics have been seeded in managed staging and no draft content is published to students.

## Automated verification added
- `backend/test_ai_tutor.py`: prompt/history bounds, provider host and credential validation, redirects, disabled-by-default, auth/CSRF and session-derived class.
- `backend/test_ai_tutor_quota.py`: estimated cost, missing pricing fail-closed, request/spend limits and platform budget limits.
- `backend/test_lesson_content.py`: entitlement enforcement, no answer-key leakage, practice feedback/history, completion and admin route auth.
- `backend/test_postgres_student_journey.py`: disposable PostgreSQL test registers a synthetic student through the HTTP route, mocks identity email delivery, verifies email, logs in, creates a synthetic published lesson and entitlement, reads notes, answers practice, records completion, checks dashboard progress, starts/submits an assessment and checks results. A second test exercises concurrent database quota reservations.
- `backend/test_postgres_schema_integration.py` updated to check all 17 numbered migrations plus baseline and new tables.
- Workflow `.github/workflows/secondary-school-platform.yml` now runs the PostgreSQL student journey test.
- A prior run showed the registration-to-results test body reached teardown successfully; teardown failed because published assessments are intentionally immutable. The fixture cleanup was corrected to leave the immutable synthetic assessment in the disposable CI database. Await the new run before declaring the suite green.
- No arbitrary local shell/Codespaces execution tool is exposed in this session. GitHub Actions is the executable verification source; source inspection alone is not a test pass.

## Outstanding work and gates
1. Wait for current CI on head `aa2ddb80ebf550136f41084615aed47c80f3d823`; inspect failed job logs and fix failures. Do not claim current head passed before success.
2. Add independent authenticated browser acceptance using synthetic test fixtures and a disposable database. Existing staging Playwright suite remains eight anonymous checks only.
3. Complete AI provider pricing verification and add provider-specific budget reconciliation/alerts; keep AI disabled until private credentials are set by the owner and tests pass.
4. Complete AI content retrieval/grounding against approved lesson sources, teacher moderation, accessibility and answer-quality evaluation.
5. Add automatic TTS only after selecting a provider, confirming pricing and implementing spend/retention controls. Until then use recorded or externally generated audio uploads through the private review workflow.
6. Capture actual subject PDFs and topic sequences for all six subjects and all applicable class cohorts. Resolve the SSS2 viewer extraction issue and SSS3 source gap. Produce original lesson packs, practice banks, answer keys and podcasts, with teacher review and verified term allocation.
7. Finish the student UI for lesson catalogue, history, progress detail, tutor conversation, podcast library and results; test all states on mobile.
8. Complete admin UI usability, role/CSRF negative tests, private audio playback tests and content lifecycle tests.
9. Rehearse migrations 014–017 on a disposable Neon branch; inspect migration hashes and idempotency before any managed staging application.
10. Run controlled SMTP and Paystack sandbox tests, verify the notification outbox worker is scheduled/monitored, and keep live payments disabled.
11. Complete NDPA/privacy, guardian consent, child safeguarding, security, accessibility, backup/restore and release reviews.
12. No production deployment or public student onboarding without separate explicit authorization.

## Current state
This increment is committed to the development branch only. It is not yet a complete populated student product, not deployed to staging, and not production-ready. Last managed staging database snapshot remains six subjects, zero topics, zero students and one owner admin; no managed database writes were made during this increment.


---

# Continuation checkpoint — 6 November 2026 (AI lesson grounding and verified CI)

## Additional implementation
- AI tutor can now accept an optional published lesson topic ID. `lesson_content.get_tutor_context` checks the student's entitlement and retrieves only approved content attached to a published topic. It bounds the retrieved reference to 4,000 characters and keeps it separate from unverified learner-provided context.
- AI tutor spend reservation includes the retrieved lesson reference before the provider call, so the cost estimate covers the actual bounded prompt.
- Student home UI now lets the learner optionally supply an unlocked topic ID; changing topic clears the in-page conversation history to avoid mixing lesson contexts.
- Added tests for entitlement-gated lesson retrieval and route-level tutor grounding.
- Admin lesson studio status label now reflects that draft authoring is connected.

## Verification evidence
- GitHub Actions run `42298238045` for commit `3456ef8531c9f95960f153464e981528616a9afa` completed successfully:
  - Unit/security tests passed.
  - Student and admin frontend JavaScript syntax checks passed.
  - All numbered migrations rehearsed successfully on disposable PostgreSQL.
  - PostgreSQL schema integration tests passed.
  - Existing assessment/payment end-to-end tests passed.
  - Synthetic student registration → email verification (mail sender mocked) → login → lesson entitlement/content → practice answer → progress → assessment submission → result-history journey passed.
  - Concurrent database AI quota reservation test passed.
  - Container image build passed without publishing.
- The current branch head at this checkpoint is `a16ad096487215d3fa379aa84eb7b43870cfa8bb`. The only commit after the fully passing code/test commit `3456ef8531c9f95960f153464e981528616a9afa` is an admin UI status-label text correction; its own CI was still running when recorded. Await that run before calling the latest head green.

## Evidence boundaries
- CI tests run against disposable PostgreSQL and synthetic fixtures. The email-verification delivery was mocked; no real email was sent.
- No external AI provider request was made; no provider key/model pricing has been configured. The tutor remains disabled by default.
- No actual TTS audio was generated; private podcast workflow requires a recorded or externally generated file upload, followed by review.
- No NERDC topics/lesson drafts were inserted into managed staging. Two SS1 source documents (English Language and Biology) have topic maps and one original draft lesson each; all remain unreviewed and unpublished.
- SSS2 official viewer links for several subjects are identified but PDF text remains unavailable; SSS3 class-specific sources are still outstanding.
- No managed Neon migrations 014–017 were applied, no Render deployment was triggered, and production/main remain untouched.


---

# Continuation checkpoint — 6 November 2026 (isolated migration rehearsal)

## Migration rehearsal
- Created a separate Neon child branch `think-tank-migration-rehearsal-20261106` (branch ID `br-plain-band-ba3mrbzi`) from the managed staging branch at its current parent snapshot. The rehearsal branch is not the staging branch and is not the project default.
- Confirmed the child branch reached `ready`.
- Applied the DDL from migrations 014–017 to the child branch database only, using one transaction with individual statements. The DDL completed successfully.
- Verified all seven expected new tables exist: `student_ai_tutor_usage`, `topic_lesson_content`, `lesson_practice_questions`, `student_topic_progress`, `student_lesson_practice_attempts`, `podcast_scripts`, and `ai_tutor_platform_usage`.
- Found a replay-safety issue in migration 015: its explicit UNIQUE constraint addition was not guarded. Updated migration 015 on this development branch to add the constraint inside a catalog-checked DO block. Applied the guarded block against the rehearsal branch where the constraint already existed; it completed successfully without duplicate-constraint failure.
- This is a targeted DDL rehearsal, not yet a full automated run of the repository migration runner against a fresh Neon child branch. The disposable PostgreSQL GitHub Actions migration suite remains the canonical full replay test.
- No migrations were applied to the managed staging parent, production, or main branch. No staging deployment was triggered.

## Remaining release work (still open)
- Capture and map actual NERDC documents and cohort applicability for all 18 subject/class tracks; only SSS1 English Language and Biology have captured topic maps at present. SSS2 subject pages list the relevant subjects, but individual curriculum PDFs remain uncaptured; class-specific SSS3 documents remain unresolved.
- Create original, teacher-reviewed lesson libraries, practice banks and answer keys for the remaining subject/class tracks. No unverified topics or guessed term mappings are to be published.
- Complete authenticated browser-level registration-to-results tests; current evidence is API-level PostgreSQL acceptance with email delivery mocked.
- Complete automatic TTS only after selecting a provider/API workflow that is supported beyond the near-term deprecation of the currently documented Speech endpoint; implement provider-specific price accounting, quota reservations, private storage and review before enabling it.
- Finish the student-facing results/history and podcast library experiences, then run mobile browser checks.
- Do not claim staging-ready or production-ready until these gates, privacy/safeguarding review, provider configuration and staging migration/deploy checks are complete.


## CI result — 6 November 2026
- Development code commit `d6177d616ecab8201217665d14a1760806e6e36a` passed GitHub Actions run `42299148536`.
- Unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL migration rehearsal, schema integration, assessment/payment end-to-end, and synthetic registration-to-results journey all passed.
- Container build completed successfully without publishing an image.
- Run: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42299148536
- The registration journey remains API-level with mocked email delivery; this does not substitute for authenticated browser testing or real SMTP.


---

## Continuation checkpoint — 7 November 2026 (student progress dashboard and podcast library)

### Verified branch and CI
- Development branch: `secondary-school-platform-foundation`.
- Current branch head: `905171f7a55254887c9cc905449598bc96403a58`.
- PR #1 remains open, draft and unmerged; `main` is untouched.
- Exact-head GitHub Actions push run `42412752132` and PR run `42412756438` both completed successfully.
- Successful CI covered unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL replay of all 17 migrations, schema integration, assessment/payment E2E, synthetic registration-to-results student journey and a non-publishing container build.
- Earlier progress-dashboard commit `94ee5ac542a611c133cee70cd10a5aadd2552c65` also passed exact-head CI (push run `42412578500`, PR run `42412582538`).
- The podcast UI test initially failed due to Python string escaping in commit `b37c0d8db86f4d38ead421dbd62a1dfa58a9e4b4`; the failure was isolated to test syntax, not application behavior. It was corrected in `905171f7a55254887c9cc905449598bc96403a58`, and the exact-head CI runs above passed.

### Completed engineering increments
1. Student progress dashboard:
   - Replaced the disconnected progress placeholder with live values from the authenticated `/api/v1/student/dashboard` endpoint.
   - Displays completed lessons, practice attempts, assessment attempts and average graded score.
   - Shows per-subject completion bars and recent lesson activity linked to the lesson page.
   - Does not invent listening-time metrics; the UI explicitly says listening time is not measured.
   - Added static UI coverage in `backend/test_release_foundations.py`.
2. Student podcast library:
   - Added `podcast_production.list_student_podcasts(student_id)`.
   - Added authenticated `GET /api/v1/student/podcasts`.
   - Listing requires an active lesson entitlement, a published topic, an approved podcast audio asset and an approved podcast script linked to that asset.
   - Added a student-facing Podcast library page. Playback requests use the existing CSRF-protected short-lived private audio access route; no permanent storage URL is exposed.
   - Added service, route-auth and UI wiring tests.
   - The staging bucket currently contains no objects, so the library is expected to show an empty state until licensed audio is uploaded and reviewed.

### Current provider state — read-only recheck
- Render service `learnwise-staging-api`, ID `srv-dbkqcmt9fdbs73c2kdpg`, remains on `secondary-school-platform-foundation`; auto-deploy is off and the service is not suspended.
- Latest Render deployment remains `dep-dbn2dcrl550s73f9ahag`, live on commit `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`, completed `2026-11-06T19:13:13.356186Z`. No deployment was triggered for the new student UI/API work.
- Render health-check path remains blank. The last owner-supplied `/health` payload was `{"mode":"database","service":"secondary-school-api","status":"ok"}`; no new external health request was performed in this checkpoint.
- Neon project `learnwise` / ID `spring-cloud-84267029`; staging branch `think-tank-staging` / ID `br-still-cherry-baz7g5hk` remains ready.
- Read-only aggregate counts on staging: 13 migration records, 6 subjects, 0 topics, 0 students, 1 administrator and 6 audit events.
- Private bucket `learnwise-private-audio` exists with private access and zero objects.
- Do not rerun owner bootstrap; the owner administrator already exists.
- Repository migrations 014–017 have passed disposable PostgreSQL CI and an isolated Neon rehearsal, but are **not recorded as applied to managed staging**. Do not deploy code requiring these migrations until a reviewed migration/deployment plan and the required owner approval are in place. Do not replay migrations autonomously.

### Current limitations and next engineering work
- The progress and podcast pages are committed and CI-verified, but are not deployed to Render.
- The podcast library has no live audio to display; approved, licensed content and private storage E2E remain outstanding.
- Continue with mobile/accessibility improvements, assessment results detail, authenticated synthetic-browser acceptance, admin CMS/assessment authoring and support workflows, and private audio route/range/revocation tests.
- Do not send prompts to an external AI provider or enable AI tutoring; provider credentials/pricing, quota alerting and privacy/content QA remain pending.
- Keep student registration and checkout disabled. SMTP delivery, Paystack sandbox, outbox scheduling/monitoring, NERDC source rights and 18-track mapping, qualified teacher sign-off, NDPA/DPIA, guardian consent, safeguarding/legal review, backup/restore, monitoring, independent security review and production approval remain open.
- The owner-reported eight anonymous staging Playwright checks and authenticated admin page checks remain owner-reported evidence; the report/traces were not independently retrieved.
- Never claim production readiness from CI, the staging health response or anonymous browser checks alone.

### Safety and handoff
- Keep PR #1 open, draft and unmerged; do not modify `main` or the legacy university Telegram bot.
- No Render deployment, Neon staging migration, environment-variable change, payment, object upload, student-account creation or production action was performed in this checkpoint.
- At the next session, re-fetch the branch head, PR, exact-head CI and provider state before editing. Continue with the highest-priority safe engineering task and append a dated checkpoint after its exact-head tests pass.


---

## Continuation checkpoint — 7 November 2026 (podcast playback authorization hardening)

### Exact-head verification
- Current development branch head: `090438017e7b326c2327a995036278c3bb90ea8e`.
- GitHub Actions push run `42412897995` and PR run `42412902759` both completed successfully on this exact head.
- Both jobs passed: unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL replay of migrations 001–017, schema integration, assessment/payment E2E, synthetic registration-to-results journey and container build without publishing.
- The earlier exact-head student progress/podcast library run `42412752132` and PR run `42412756438` also passed.

### Additional security correction
- The student topic-detail endpoint now hides podcast audio unless the asset is linked to an approved podcast script.
- The private audio access endpoint independently enforces the same approved-script condition for `podcast_audio`, in addition to asset review, published topic and active entitlement checks. A caller cannot bypass the library by guessing an asset ID.
- Added a route test proving direct playback is rejected when there is no approved linked script.
- No external audio provider was contacted and no audio object was uploaded.

### Current provider snapshot
- Render remains unchanged: service `learnwise-staging-api` is configured to the development branch, auto-deploy is off, and latest live deployment remains `dep-dbn2dcrl550s73f9ahag` on `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`. No deployment was triggered.
- Neon staging branch `think-tank-staging` remains ready. Read-only aggregate counts: 13 migration records, 6 subjects, 0 topics, 0 students, 1 administrator, 6 audit events. Private bucket `learnwise-private-audio` remains empty.
- Repository migrations 014–017 remain unapplied to managed staging. Do not deploy the newer code or replay these migrations until a reviewed plan and owner approval exist.
- Last owner-supplied staging health response remains `{"mode":"database","service":"secondary-school-api","status":"ok"}`; it was not re-requested in this engineering increment.

### Remaining work
- Build authenticated synthetic-browser acceptance using disposable fixtures; current staging browser suite is eight anonymous/read-only checks reported passed by the owner.
- Complete mobile and accessibility checks, assessment result detail and history UX, admin CMS/assessment authoring/finance/support workflows, student export/correction/deletion UAT, and private audio range/revocation/provider tests.
- Keep AI tutoring disabled until provider, pricing, budget alerting, privacy and content-quality gates pass.
- Keep student registration and checkout disabled until SMTP and Paystack sandbox acceptance and safeguarding/privacy approvals pass.
- External blockers remain authorised NERDC source materials and digital reuse rights for all 18 class/subject tracks, qualified teacher sign-off, NDPA/DPIA and child/guardian consent review, safeguarding lead and Nigerian legal review, monitoring/alerts, backup/restore, independent security review and explicit production approval.

### Safety
- PR #1 stays open, draft and unmerged. `main` and the legacy university Telegram bot remain untouched.
- No deployment, managed staging migration, environment-variable change, account creation, payment, storage upload or production action occurred.


---

## Continuation checkpoint — 7 November 2026 (assessment history UX)

- Tested application commit: `199c4e52bfd86050df4058a50593846745434fbd`.
- Exact-head GitHub Actions push run `42413078275` and PR run `42413082270` both passed.
- Student assessment history now distinguishes attempts from completed assessments and displays status, score/maximum score, question count, percentage, pass/fail, human-review flag and submitted/started timestamp. Empty/error states remain explicit.
- Added static UI coverage for these source fields. Existing authenticated assessment-history API remains the data source; no score or result is fabricated.
- The earlier progress dashboard, podcast library and podcast-script playback authorization remain present and covered by the previously passing exact-head CI runs.
- No staging deployment or database migration was performed. Render remains on the previous live SHA; managed Neon staging remains at 13 migrations while repository CI rehearses all 17 migrations on disposable PostgreSQL.
- At the next session, fetch the live branch head and latest CI before editing. Continue with accessible/mobile student experience and admin curriculum/assessment authoring, then synthetic authenticated browser acceptance.


---

## Continuation checkpoint — 7 November 2026 (saved lessons)

### Exact-head CI
- Tested application commit: `8e1f838c34d5dcc55c6358e74c97928566dcb622`.
- Exact-head push run `42413332222` and PR run `42413335065` both passed.
- Passed unit/security tests, frontend/admin JavaScript syntax, disposable PostgreSQL replay of migrations 001–018, PostgreSQL schema integration, assessment/payment E2E, synthetic registration-to-results journey and non-publishing container build.
- The initial run after adding migration 018 correctly applied all 18 numbered migrations but exposed a stale schema integration expectation (19 total records including baseline, not 18). Updated the assertion and latest exact-head runs passed.

### Completed saved-lessons feature
- Added migration `018_student_saved_topics.sql` with a private per-student bookmark table and recent index.
- Added `student_saved_lessons.py` list/save/remove service functions.
- Added authenticated GET and CSRF-protected POST/DELETE student routes.
- Replaced the empty Saved Lessons placeholder with a working student page; published catalogue cards now have a Save lesson action. Students can open or remove their bookmarks.
- Saving is idempotent; only published, curriculum-published topics can be saved or listed. The UI uses safe DOM text insertion and URL-encoded topic IDs.
- Added service, route-security, UI and schema-integration tests.

### Provider state and migration boundary
- Render staging was not deployed. Latest live service deployment remains `dep-dbn2dcrl550s73f9ahag` on `0f343fff800b619fdaff76f5ee97225ec6c3dbdf`; auto-deploy remains off.
- Managed Neon staging remains at 13 migration records, 6 subjects, 0 topics, 0 students, 1 administrator and 6 audit events. Private bucket `learnwise-private-audio` remains empty.
- Repository migrations 014–018 are verified only in disposable CI/rehearsal databases and are not applied to managed staging. Do not deploy new code to staging or apply migrations until compatibility, reviewed sequencing, owner approval and safe backup/rollback are confirmed.
- No health request was performed in this increment; the last owner-supplied health response remains status `ok`, mode `database`, service `secondary-school-api`.

### Next safe engineering work
- Continue mobile/responsive and accessibility QA for student progress, saved lessons, podcast library and assessment history.
- Improve assessment result detail/review UX and complete admin CMS/assessment authoring, finance and student-support workflows.
- Add authenticated synthetic-browser journeys on disposable fixtures; do not create test accounts on managed staging.
- Complete private audio provider/range/revocation E2E only with approved non-production test storage; current staging bucket is empty.
- Continue to hold registration/checkout, SMTP, Paystack sandbox, AI provider, external curriculum publication, student media uploads and production release behind their existing gates.


---

## Continuation checkpoint — 7 November 2026 (admin authoring, privacy, finance and release operations)

### Tested application milestone
- Latest fully tested application commit: dd7b620676c4312aa9540a89d19be71381f71ec5.
- Exact-head push CI 42415624459 and PR CI 42415628254 both passed.
- CI passed unit/security tests, JavaScript syntax, baseline plus migrations 001–019 on disposable PostgreSQL, schema integration, assessment/payment E2E, synthetic registration-to-results, authenticated/anonymous Playwright browser tests and non-publishing container build.
- The authenticated browser job creates only a disposable CI owner administrator and synthetic subjects in its temporary PostgreSQL service. It does not touch managed staging.
- Current branch has subsequent documentation-only updates recording this verified state; fetch latest branch head before making more changes.

### Software work completed in this increment
1. Admin mobile/accessibility: bottom navigation at narrow widths, safe-area spacing, skip link, named navigation landmark, visible focus, reduced-motion and forced-colour support. Student account fields now expose accessible labels and password-manager autocomplete.
2. Curriculum: existing protected admin interface and API-backed source/topic draft/review/publish flow retained. The UI notice now distinguishes persisted API workflows from local-only previews.
3. Assessments: added admin_assessments.py and protected admin/assessments.html workspace. Owner/editor can create drafts and add validated single-choice, multiple-select, true/false, numeric and exact-text questions; reviewer/owner publication is permission-gated; published versions remain immutable. Detail API does not return answer keys.
4. Finance: added read-only ledger summary and unverified/stale payment exception counts to admin operations. No provider reconciliation, charge, refund or payment write is performed by the dashboard.
5. Student data rights: migration 019; authenticated student request intake/history/withdrawal; scoped self-service JSON export; restricted admin triage and response notes. Deletion is a tracked request only, never automatic.
6. SMTP: mocked STARTTLS/SSL transport tests added. No actual SMTP credentials/mailbox delivery has been verified.
7. Paystack: existing server-side verification contract tests remain. No real Paystack sandbox account/key or provider-side charge/webhook/refund run has been performed.
8. Private audio: existing S3-compatible private upload/range/delete and token/entitlement security tests remain mock-backed. Managed staging audio bucket is empty; no real provider E2E playback/revocation test has been performed.
9. Operations: added guarded local-only restore rehearsal script and backup/recovery/monitoring runbook. No managed backup restore has been executed.

### Migration and provider state
- Canonical repository migrations: 001–019 plus baseline (20 entries in disposable CI).
- Managed Neon project learnwise, branch think-tank-staging (br-still-cherry-baz7g5hk): exactly migrations 001–013 recorded in learnwise_migration_history; 0 students, 1 admin, 6 subjects, 0 topics, 6 audit events.
- Neon branch think-tank-migration-rehearsal-20261106 (br-plain-band-ba3mrbzi) also contains only 001–013. It is not a rehearsal of 014–019.
- Migrations 014–019 pass disposable CI but are not applied to managed staging.
- Render service learnwise-staging-api: auto-deploy off; latest live deployment dep-dbn2dcrl550s73f9ahag, commit 0f343fff800b619fdaff76f5ee97225ec6c3dbdf, finished 2026-11-06T19:13:13Z. Do not trigger a deployment without explicit owner approval.
- Public /health not directly verified in the last check. Web open returned “URL is not accessible by this tool”; Render HTTP metrics filtered to /health returned no data. Treat this as unavailable evidence, not as a confirmed outage. Service metadata healthCheckPath is empty.

### Remaining release blockers
- No authorised NERDC curriculum materials/licence and no independent qualified teacher sign-offs.
- No live SMTP delivery/account-recovery proof.
- No Paystack sandbox E2E with authorised test credentials.
- No real private audio provider E2E; managed bucket empty.
- No verified guardian identity/consent process, completed NDPA/DPIA, retention schedule, Nigerian legal review, child-safeguarding policy/lead or processor/cross-border review.
- Self-service JSON export is synchronous; bulk export worker, streaming, private archive/checksum manifest, signed URL lifecycle and automated export expiry remain outstanding.
- Correction/deletion fulfilment remains a human/legal workflow; no automatic deletion.
- Backup/restore runbook exists, but managed restore and approved RPO/RTO/retention are outstanding.
- Monitoring alert delivery/incident drill and independent security review remain outstanding.
- Staging database must be reconciled/upgraded safely from 013 to 019 only after backup, compatibility review, isolated branch rehearsal and explicit owner approval.
- Staging deployment approval and production-launch approval are separate decisions. Neither has been granted.

### Immediate next actions
1. Fetch latest branch head, current exact-head CI and PR state.
2. Wait for any documentation-only commits' CI to finish; do not claim a later commit is tested unless its exact-head push and PR runs pass.
3. Continue the remaining software gap analysis, especially assessment draft correction/versioning and admin student support, then add browser tests.
4. Prepare but do not execute an isolated Neon migration rehearsal for 014–019 until owner authorises it; current managed staging remains at 013.
5. Obtain the required provider accounts, licensed NERDC sources, teacher/legal/safeguarding reviewers and written deployment approval through secure external channels.
6. Do not merge PR #1, deploy staging, change environment variables, run managed migrations, activate live payments, upload media or launch production without explicit owner approval.


---

## Continuation checkpoint — 7 November 2026 (authenticated student rights journey verified)

- Latest fully tested application commit: a057289c4930b86b6bdd5176bd71e61a9536f044.
- Exact-head push run 42416064502 and PR run 42416068375 both passed.
- 246 unit/security tests passed; Python compileall, JavaScript syntax and backup script shell syntax passed.
- Disposable PostgreSQL baseline plus migrations 001–019, schema integration, assessment/payment E2E and synthetic student journey passed.
- All 14 Playwright tests passed. The authenticated student flow signs in using an ephemeral synthetic student, submits and withdraws an access/export request, downloads a scoped JSON data export, and asserts password hashes, answer keys and provider payloads are absent. The admin assessment create/question/publish journey and restricted data-rights queue also pass.
- Browser acceptance uses only disposable CI PostgreSQL fixtures; no live staging account or payment is created.
- An async form-reset bug found by the browser test has been fixed by capturing the form reference before awaiting the API.

Fetch latest branch head and exact-head CI before any further changes. Documentation-only updates after this tested application commit must not be represented as new application test evidence unless their own exact-head workflows pass.


### Additional migration checksum evidence — 7 November 2026
Read-only comparison of managed Neon learnwise_migration_history.source_blob_sha against the development branch's canonical backend migration GitHub blob SHA returned exact matches for all applied migrations 001–013 (13/13). No source drift was detected in the applied sequence. Pending migrations 014–019 remain unapplied; they still require an upgrade rehearsal from the actual 001–013 state, backup/rollback evidence and explicit owner approval.


### Latest provider and CI checkpoint — 7 November 2026
- Current branch head ee2cc4306279772ecb05a3813eb33266c134d497.
- Exact-head push CI 42416698937 and PR CI 42416702456 both passed.
- New read-only staging-health job runs on every push/PR workflow and verified public /health: HTTP 200, JSON status=ok, mode=database, service=secondary-school-api. This matches the previously recorded healthy status.
- CI passed 246 unit/security tests, Python compileall, JS/shell syntax, all 19 numbered migrations on disposable PostgreSQL, local backup/restore to a separate disposable DB (20 migration-history rows restored), schema integration, assessment/payment E2E, synthetic student journey, 14 Playwright tests and non-publishing container build.
- Read-only Neon comparison confirmed exact GitHub blob SHA matches for all 13 applied managed-staging migrations. Migrations 014–019 remain unapplied.
- Render remains on live deployment dep-dbn2dcrl550s73f9ahag, SHA 0f343fff800b619fdaff76f5ee97225ec6c3dbdf, completed 2026-11-06T19:13:13.356Z. Development branch is 225 commits ahead. No failed/in-progress deployment event; auto-deploy off; no deploy performed.
- Public health is verified by CI; Render's healthCheckPath itself is still empty and was not changed.


### Latest branch head and exact CI — 7 November 2026
Current branch head 1419ed4b8c6011ad5d30ea9299a36c2816e1aa3c. Application code remains at the tested a057289c4930b86b6bdd5176bd71e61a9536f044; subsequent changes are documentation/workflow evidence updates. Exact-head push 42416831355 and PR 42416833832 both passed, including the read-only public staging health job, migration replay, local backup/restore rehearsal and authenticated browser suite.


### Final continuation pointer — 7 November 2026
Latest repository/PR head is 2098d7ad37b830a84a1120654afc56b5152ae4ef (documentation/PR evidence only); latest tested application commit remains a057289c4930b86b6bdd5176bd71e61a9536f044. Exact-head push CI 42416959890 and PR CI 42416965208 both passed, including public /health, disposable backup/restore, all migrations in CI and authenticated browser journeys.


### Handover pointer — 7 November 2026
Current branch/PR head: fc77dbc714af2103b50f58c02bff844556a776ad. Exact-head push 42417089283 and PR 42417094553 passed. This branch head contains documentation/PR-status changes only; latest tested application code remains a057289c4930b86b6bdd5176bd71e61a9536f044. Latest public staging health is HTTP 200, status=ok, mode=database, service=secondary-school-api. Render remains on its prior live deployment; no managed migration or deployment was performed.


## Authoritative continuation checkpoint — 8 November 2026

### Project identity and safety
- This remains the Think Tank SS1–SS3 secondary-school tutorials platform in `JephterAce/Year-1-Tutorial`, branch `secondary-school-platform-foundation`. Do not confuse it with the legacy university Telegram subscription bot.
- PR #1 remains open, draft and unmerged. Do not modify `main`, force-push, merge the PR, expose secrets, deploy production, purchase/upgrade services, or perform destructive operations without separate owner approval.
- Render workspace `Emmanuel's workspace` (`tea-da2svh0ae00c73cs4qq0`) is confirmed for read-only inspection and approved staging-only verification.

### Render status
- Service `learnwise-staging-api`, ID `srv-dbkqcmt9fdbs73c2kdpg`, URL `https://learnwise-staging-api.onrender.com`, branch `secondary-school-platform-foundation`, Frankfurt, free plan, auto-deploy disabled.
- Latest Render deployment is `dep-dbo22jp5efls73cm1sb0`, live at commit `c5805a6fc463fd040e64e8223d58ed3dbf37d143`, completed 2026-11-08T07:14:47Z. The later development commits have not been deployed.
- Public health was verified by the GitHub Actions staging-health job: HTTP 200, JSON status `ok`, mode `database`, service `secondary-school-api`. Render logs show Gunicorn listening on port 8000 and Render reporting the service live. Render's own `healthCheckPath` remains empty; do not change it without a separate review.

### Managed Neon status
- Project `learnwise` (`spring-cloud-84267029`), staging branch `think-tank-staging` (`br-still-cherry-baz7g5hk`), database `learnwise`.
- Read-only inspection verified migration history 001–019. Every one of the 19 recorded `source_blob_sha` values exactly matches the corresponding canonical backend migration GitHub blob SHA.
- Read-only counts on managed staging: 6 subjects, 0 topics, 0 students, 1 active admin, 0 student data-rights requests.
- Backup branch `think-tank-staging-backup-2026-11-08` (`br-super-haze-bazf13ia`) is ready. Existing older rehearsal branch `think-tank-migration-rehearsal-20261106` remains separate.
- New isolated rehearsal branch `think-tank-migration-rehearsal-2026-11-08` (`br-divine-bread-bah58gvn`) was created from staging at migrations 001–019. Migration `020_private_student_export_approval.sql` was applied only there. Read-only schema inspection confirmed its six columns, four check constraints, approver foreign key and approved-queue index. A rehearsal migration-history row records blob SHA `3ee86c0d909f429f6ca5787c47b51f86dfdf9a13`, matching the development migration file. Managed staging remains at 019; do not apply 020 without explicit owner approval.

### New development-branch implementation
- Added `backend/migrations/020_private_student_export_approval.sql` for a separate export approver, approval timestamp, manifest key, worker attempt metadata and safety constraints.
- Added `backend/admin_data_exports.py` and registered it in the Flask app. It supports queued individual/filtered bulk export requests, listing, separate-administrator approval, retry, cancellation and signed-download URL issuance. Export request caps are five per admin per 24 hours, one bulk per day and two active jobs.
- Added restricted admin page `/admin/exports` and links from the data-rights and operations pages.
- Added `backend/student_bulk_export.py`: one repeatable-read/read-only snapshot, server-side student cursor, NDJSON or CSV output, multipart upload, SHA-256 manifest, 1,000-student cap, five-minute maximum signed URLs, 24-hour default expiry and expiry cleanup. It uses separate `DATA_EXPORT_AWS_*` credentials and `DATA_EXPORT_STORAGE_BUCKET`, never the audio bucket.
- Worker is fail-closed and disabled unless `DATA_EXPORT_WORKER_ENABLED=true`. No export bucket, credentials or scheduled worker have been provisioned. No real export job has been run. Subject-scoped bulk exports are explicitly rejected until every exported record type can be filtered correctly.
- Two-person approval is mandatory: requester and approver must be different active administrators. Export capabilities are owner-only; managed staging currently has one active owner, so no admin export can be approved until a second owner is provisioned through the controlled offline process. Never bypass this control.
- Student self-service export remains separate and scoped to the authenticated learner. Data-rights deletion requests remain intake-only and never automatically erase accounts or records.

### CI status for this increment
- The first run that included the new export tests was workflow run `42459497431` at commit `e7f4d41deeed17549afb9fb76c4e0ef1eae08eca`. `staging-health` and `container-build` passed. `api-tests` failed on two new test fixtures that omitted `export_scope`.
- The fixtures were corrected in subsequent development-branch commits. The available GitHub connection has not returned a fresh exact-head workflow run/status for the corrected head. Do not claim the new export code is CI-passed until a fresh exact-head run completes successfully.
- The new code has not been deployed to Render. Auto-deploy remains off.

### Remaining build and release gates
1. Obtain a fresh exact-head CI run and fix every failure before staging deployment.
2. Rehearse migration 020 from the current 001–019 staging state (the isolated rehearsal branch already has the additive DDL applied and inspected); then obtain explicit owner approval before applying it to managed staging.
3. Configure a dedicated private export bucket, encryption-at-rest, least-privilege bucket-scoped credentials, retention/lifecycle policy and worker scheduling. Provision a second owner approver offline. Keep the worker disabled until all of these are verified.
4. Complete SMTP delivery and password/account recovery E2E; Paystack sandbox checkout/webhook/entitlement/reconciliation; private audio storage/playback acceptance.
5. Obtain authorised NERDC materials/licensing, curriculum mapping and teacher review. Staging currently has zero topics; do not publish unlicensed or unreviewed content.
6. Complete child safeguarding, guardian consent/age verification, NDPA assessment/DPIA, retention schedule and Nigerian legal review.
7. Complete managed backup/PITR restoration drill with measured RPO/RTO, monitoring/incident-alert verification and independent security review.
8. Run authenticated browser acceptance against the newly deployed staging commit after migration 020 and all environment prerequisites are approved.
9. Update this file, `STATUS.md`, `EXECUTION_AUDIT.md` and `RELEASE_GATE_REGISTER.md` after each verified milestone.

### Required reporting format
For each continuation, report Completed / Verified / Passed / Failed / Outstanding / Blocked / GitHub / Render / Neon / Approval required. Distinguish source-code implementation, disposable CI evidence, isolated Neon rehearsal, managed staging state and production state. Never call the platform launch-ready while any external/legal/safeguarding/security gate remains open.


### Final repository pointer for this checkpoint — 8 November 2026
- The development branch head immediately before this final handover pointer was `c421b4e305731c8850b6b3bd93e856578fbbd27c`; it was 30 commits ahead of the live Render deployment SHA `c5805a6fc463fd040e64e8223d58ed3dbf37d143`.
- `STATUS.md` was updated at commit `280927402ffaf68c6cae46a8bcfc86e74fdb7d50` to record that pointer and the CI caveat. This master-file update itself will create a newer branch head; verify the resulting latest SHA before any subsequent action.
- PR #1 is still open/draft/unmerged. The new export implementation has not been deployed. A fresh exact-head CI run remains mandatory before migration 020 or staging deployment.


### CI correction checkpoint — 8 November 2026
- Workflow 42460006986 at commit 1316c1d2fa789c2f67eb389ac10605f0489ac374 passed 260 unit/security tests, public staging health (HTTP 200/status=ok/database/secondary-school-api) and non-publishing container build. Its syntax step failed on a literal escaped newline in the new exports admin page.
- Fixed the page in commit 81d33094f0506a71c9f72984133075fa75c84252. A subsequent GitHub read-back confirms the literal `\\n` is gone and the source has a real line break between the two declarations. No fresh exact-head CI result has been returned yet; do not assume the corrected head passes syntax or the later migration/backup/PostgreSQL/browser steps.
- Current branch head at this checkpoint is 81d33094f0506a71c9f72984133075fa75c84252, 54 commits ahead of the live Render SHA. PR #1 remains draft/unmerged; no new deployment or managed migration occurred.


### Green CI checkpoint and export browser acceptance — 8 November 2026
- Run 42460191786 (run 1180, commit 7de9dd1d0da160e634673fc813a16befb147e383) completed fully green: API tests, staging health and non-publishing container build all succeeded. The API job passed 260 unit/security tests, syntax, migration replay/idempotency for all 20 numbered migrations, backup/restore, PostgreSQL schema integration, assessment/payment E2E, student journey and the existing authenticated/anonymous Playwright suite.
- Run 42460225765 (run 1184, commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3) includes the additional owner export request/cancel/self-approval browser acceptance and anonymous exports-page redirect check. At the latest inspection, every step through the student journey had passed; Playwright installation/browser tests were still in progress. Recheck the run before marking this additional UI test passed.


### Full exact-code CI pass — 8 November 2026
- Run 42460225765 (run 1184) completed fully green at code commit 5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3: api-tests, staging-health and container-build all succeeded.
- It passed 260 unit/security tests; Python/JS/shell syntax; all 20 numbered migration replays and idempotency; local backup/restore; PostgreSQL schema integration; assessment/payment E2E; registration-to-results; and all anonymous/authenticated Playwright browser checks, including the new private export page, bulk request/cancel, no self-approval and anonymous redirect tests.
- Staging health returned HTTP 200/status=ok/mode=database/service=secondary-school-api. The container build was non-publishing. The tested code commit is included in the current development branch; later commits update documentation only.
- This is disposable CI evidence, not a deployment or real-provider acceptance. Render remains on c5805a6; managed Neon remains at migrations 001–019; migration 020 exists only on the isolated rehearsal branch. Do not promote without explicit owner approval.


### Final repository reconciliation — 8 November 2026
- Latest tested application-code commit: `5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3`, workflow 42460225765 fully green.
- Current development branch head immediately before this final handover update: `3a5cace1db3b9de2803b18f22c4974e69c4b963d`. It is eight documentation-only commits ahead of the tested application-code commit; no application code changed after the green run.
- Render still serves commit `c5805a6fc463fd040e64e8223d58ed3dbf37d143` with auto-deploy disabled. Managed staging has 19 migration records. Migration 020 remains on isolated rehearsal branch `br-divine-bread-bah58gvn` only.
- PR #1 remains open/draft/unmerged. The current code is CI-verified but not yet deployed. Staging migration 020 and matching code deployment require separate explicit owner approval.


## Latest continuation checkpoint — 8 November 2026 (staging migration and deployment)

Owner approval was received to apply migration 020 and deploy the tested code to the existing Render staging service only. This does not authorise merging PR #1, changing `main`, deploying production, enabling live payments, provisioning paid services, or changing secrets.

### Completed and verified
- Applied `020_private_student_export_approval.sql` to managed Neon staging branch `think-tank-staging` (`br-still-cherry-baz7g5hk`), project `spring-cloud-84267029`, database `learnwise`.
- Read-only verification: migration history count 20; latest version `020_private_student_export_approval`; source blob SHA `3ee86c0d909f429f6ca5787c47b51f86dfdf9a13`; six expected columns present; four expected constraints present.
- Manually deployed Render staging service `learnwise-staging-api` (`srv-dbkqcmt9fdbs73c2kdpg`) in workspace `tea-da2svh0ae00c73cs4qq0`. Deployment `dep-dbo2l1h5efls73cnf8j0` reached `live`; build succeeded; Gunicorn started and workers booted. Branch `secondary-school-platform-foundation`, deployed head `c03b7e98aee4a046d300185eb5089b42f747a75c`.
- Application source remains the fully green CI-tested commit `5673a7f8660ef1dd0a7f5ca407e47f3d9ae3f0e3`; later commits through the deployed head are documentation-only.
- Updated `STATUS.md` with this evidence.

### Not yet verified from this execution environment
- Public Render `/health` response after deployment: the web fetch could not access the endpoint, and container outbound DNS resolution failed. Deployment-live status and Gunicorn startup do not prove HTTP 200. Recheck `https://learnwise-staging-api.onrender.com/health` from a normal browser or authenticated external runner; expected JSON is `status=ok`, `mode=database`, `service=secondary-school-api`.
- Authenticated browser acceptance against the newly deployed service: no browser/Playwright control is available in this execution environment. CI's authenticated/anonymous Playwright suite passed on the exact tested application commit, but it ran against synthetic disposable fixtures, not the live staging service.

### Safety and release state
- Keep PR #1 open/draft/unmerged and leave `main` untouched. Do not rerun `bootstrap_admin.py` or create another admin automatically.
- Export worker remains disabled. No private export bucket, dedicated credentials, worker schedule, or second owner approver has been configured. Bulk export remains unavailable until these controls are completed.
- Remaining gates: SMTP delivery and recovery; Paystack sandbox E2E; private audio real-provider acceptance; authorised NERDC source rights and teacher review; child safeguarding, guardian consent, NDPA/DPIA; Nigerian legal review; managed backup restoration and RPO/RTO; monitoring/alert delivery; independent security review; second owner administrator; private export bucket and worker scheduling.
- Staging deployment is not production readiness. No production launch or student onboarding is approved.

### Next operator actions
1. Verify public `/health` HTTP 200 and expected JSON from a network-enabled browser/runner.
2. Run authenticated browser acceptance against the deployed Render URL using an authorised existing staging admin session; do not request or expose passwords in chat.
3. Record exact outcomes and continue with provider/safeguarding/legal gates only when owner credentials, reviewers and approvals are available.


### Owner-confirmed post-deployment health — 8 November 2026
The owner opened `https://learnwise-staging-api.onrender.com/health` and supplied the response `{"mode":"database","service":"secondary-school-api","status":"ok"}`. Mark public staging health verified after deployment. The only immediate live acceptance item still outstanding is authenticated browser acceptance against the deployed Render service; do not request or receive passwords in chat.


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


## Continuation update — 8 November 2026, 16:00 UTC

Continue from the latest development branch head; do not reset, rebase destructively, merge PR #1, change `main`, or deploy production.

### Newly verified milestones
- Private-audio strict object-key and byte-range validation deployed to existing Render staging service `learnwise-staging-api`: deployment `dep-dbo9jk0u01pc73ekc330`, commit `36141466a8226a6f5e4d91b1d6a08f1ebe1d2c79`, status `live`.
- Exact-commit CI run [42478184387](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42478184387) passed all three jobs. Post-deploy health logged HTTP 200, JSON status `ok`, mode `database`, service `secondary-school-api`.
- Read-only live staging browser workflow was adjusted to trigger on updates to its own workflow file on the development branch. Run [42497224093](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497224093) passed 9/9 real-browser checks against live staging: page delivery, account controls, keyboard/mobile accessibility, anonymous API denial and admin access protection. This is not authenticated learner acceptance; no account was created or used.
- Checkpoint and STATUS files now record the above results and latest Neon audit.
- Latest fresh read-only Neon counts: 0 students, 1 active admin, 0 topics, 0 approved curriculum source records, 20 migrations. Snapshot list and staging automatic snapshot schedule are both empty. No data or recovery settings were changed.

### Critical next work
1. Do not enable public student registration. Design and implement a staging-only synthetic QA account lifecycle only after it can guarantee separate QA identity markers, owner-only auth+CSRF, reserved recipient/identity, token hashing, expiry/revocation/cleanup, audit trail, and no false guardian-consent records. Verify that synthetic QA sessions cannot access real learner data. Do not directly insert students with SQL or use the admin bootstrap.
2. Inspect current SMTP diagnostic failure logs for phase and exception class before considering any retry. The recorded SMTP attempt failed with `smtp_diagnostic_unavailable`; no delivery receipt exists. Do not retry while rate-limited. Never expose provider details or secrets.
3. Continue only non-destructive private audio/R2/Paystack test preparation until runtime credentials and provider acceptance paths are available. R2 owner-reported secrets are not independently verified; no object PUT/GET/checksum/unsigned denial/cross-bucket/deletion test has run. Audio code deployment does not prove real object upload/playback.
4. Paystack sandbox E2E requires sandbox credentials in Render and a controlled sandbox transaction; no live charge.
5. Authenticated live-staging browser acceptance remains outstanding; current live suite is intentionally read-only and anonymous. Keep write-capable browser tests confined to disposable fixtures.
6. No approved NERDC sources/topics yet; require licensing and qualified teacher review for all 18 mappings. No curriculum publication.
7. Safeguarding lead, guardian consent, NDPA/DPIA, Nigerian legal counsel, second admin, and independent security reviewer are human dependencies; do not fabricate sign-offs.
8. Managed recovery remains unverified: no Neon snapshots or schedule, backup branch is not a managed restore. Do not enable a paid schedule or alter root/default branch without explicit approval.
9. Monitoring alerts remain unverified; Render connector exposes no named alert-recipient/delivery configuration.

Keep the existing Render service on Free, auto-deploy disabled, export worker disabled, student registration disabled, and live payments disabled. No new subscriptions, paid upgrades, billable resources, domain purchase, production deployment or PR merge without explicit owner approval. Keep the user interaction minimal; only request real credentials/decisions/approvals when unavoidable.

Detailed evidence: `secondary-school-platform/DEPENDENCY_EXECUTION_CHECKPOINT_2026-11-08.md` and `secondary-school-platform/STATUS.md`.


### Latest execution addendum — 8 November 2026
- Live read-only staging browser acceptance passed 9/9 tests in run [42497224093](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497224093). Authenticated live-staging acceptance remains outstanding; no live accounts or write operations were used.
- A Neon private-audio data-plane smoke test was attempted with a 76-byte synthetic payload and a short-lived presigned PUT. The execution host could not resolve the Neon storage hostname (HTTP 000); the bucket prefix was subsequently confirmed empty. No object was uploaded. This remains blocked, not passed. The test payload SHA-256 and full result are recorded in the dependency checkpoint.
- Latest docs-only updates were recorded in `STATUS.md` and `DEPENDENCY_EXECUTION_CHECKPOINT_2026-11-08.md`. No production changes or staging application deployment were triggered.
- Latest verified full platform CI run before the newest docs-only record: [42497412130](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497412130), all jobs passed on commit `1fd1753cf571b0c20e46286dfca2451bd9b4cdaf`. Newer documentation commits have their own checks in progress; verify those before declaring the branch head green.


### Synthetic QA lifecycle design checkpoint — 8 November 2026
- Read and reviewed the live identity implementation. Existing public registration creates pending student rows and writes privacy-notice/terms acceptance records; it is not safe to reuse for synthetic QA.
- Added `STAGING_SYNTHETIC_QA_IDENTITY_SPEC.md` as the implementation contract. Required controls include staging-only flag + APP_ENV check, owner session/CSRF/permission, fixed configured QA mailbox, hashed single-use verification, explicit immutable synthetic marker, default-deny learner-data access, expiry/revocation, audit and safe cleanup.
- The initial spec was subsequently implemented, CI-tested and deployed to staging. No live synthetic account has been provisioned; authenticated live acceptance remains blocked by unverified SMTP and the unconfigured dedicated QA mailbox. Never write guardian consent or policy acceptance as a QA shortcut.
- PR workflow run [42497551018](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42497551018) passed all three jobs, including PostgreSQL migration/integration and disposable authenticated browser tests, staging health and container build. These tests do not prove authenticated live-staging acceptance.



### Synthetic QA, R2 and staging checkpoint — 8 November 2026



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



## Continuation addendum — 8 November 2026, 16:35 UTC

Current branch: `secondary-school-platform-foundation`. Latest code commit promoted to Render staging: `9367331b2ad3f0640427a9c4119779acbbc70462`. Latest documentation/workflow commit: `51e4efb152c762f9e350e4446d19dd86da8db0c5`. PR #1 remains draft/open/unmerged; main untouched.

### Synthetic QA lifecycle
- Migration 021 `021_synthetic_qa_identity.sql` is applied to Neon staging branch `think-tank-staging` with matching source blob SHA `f7a08dc396534ee7bb8be25d656bf49415ba862e`.
- Render deploy `dep-dboa96nig07c73a2dlf0` is live on commit `9367331b2ad3f0640427a9c4119779acbbc70462`.
- Owner-only staging QA issuance/revoke/expiry controls, 24-hour expiry, hashed 30-minute verification tokens, fixed configured mailbox, no consent rows, synthetic-session default deny, learner-data isolation and UI labelling are implemented.
- Push CI `42500044511` and PR CI `42500050705` passed all jobs on the deployed code commit, including disposable PostgreSQL lifecycle tests and authenticated/anonymous browser acceptance.
- No synthetic account exists. Keep `STAGING_QA_IDENTITY_ENABLED` off until a dedicated QA mailbox is configured and SMTP delivery is proven. Do not use a real learner or invent guardian consent.
- The read-only live staging browser suite was expanded to run after every development-branch push. Run `42500709060` completed with 9/9 tests passed against the live staging service after the new deployment. This checks public health, pages, anonymous denial, mobile/keyboard behavior and admin redirect/login separation; it is not authenticated live-staging acceptance.

### Current execution queue
1. Complete the latest CI runs for documentation/workflow commit `51e4efb152c762f9e350e4446d19dd86da8db0c5`; keep branch checks green.
2. Continue storage acceptance. A direct Neon storage presign was attempted earlier but the model-side network could not resolve the storage hostname. A repeat must run from the Render network using existing Render secrets. R2 and audio object upload/retrieval/checksum/unsigned-denial/delete remain unverified. Do not turn on the export worker.
3. Actual audio playback still needs a teacher-approved lesson asset and valid learner entitlement; synthetic QA accounts are deliberately blocked from learner audio.
4. SMTP/Brevo delivery is unverified; configure only through the provider/Render dashboards. Synthetic account issuance must fail closed if mail delivery fails.
5. Paystack sandbox transaction/webhook/reconciliation requires sandbox credentials and a controlled sandbox transaction; live payments remain disabled.
6. Curriculum licensing and teacher sign-off, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, second administrator and independent security review require real appointments/evidence.
7. Managed backup restoration and monitoring alert delivery require an approved recovery target/RPO/RTO and named alert recipient. No paid snapshot/monitoring resources without owner approval.

Safeguards remain: student public registration explicitly disabled; synthetic QA identity is staging-only and owner/CSRF/permission gated with a fixed configured recipient and 24-hour expiry; storage diagnostics are staging-only and owner/CSRF/permission gated; export worker disabled; live payments disabled; Render auto-deploy disabled; no production deploy; no merge; no main change; no paid upgrades; no real student data.


### Staging diagnostics controls — 8 November 2026, 16:47 UTC
- Added owner-only private storage acceptance control in /admin/operations, backed by POST /api/v1/admin/diagnostics/storage. It tests private audio and R2 export PUT/GET/SHA-256/unsigned-denial/DELETE from the Render runtime using synthetic WAV bytes. Feature flag is enabled on staging; one attempt per admin per 15 minutes. Not yet executed; owner click is required to use the signed-in admin session.
- Added synthetic QA invitation/revoke/expiry controls to the same page. The staging-only QA flag is enabled and a QA recipient is configured to the confirmed owner mailbox. Public student registration remains disabled. No QA account exists yet; owner must click the invitation control, verify the emailed link and sign in. SMTP failure rolls back the pending identity.
- Deployment dep-dboaenuc6qcc73d3lc00 is live on a9b7bacd4c3069651319df79ce95ec932a7797fc. Push CI 42501474162 and PR CI 42501478189 passed all jobs. Read-only live browser run 42501474212 passed 9/9 before environment-flag update; this docs push triggers a fresh health/browser check.
- The storage test verifies unsigned access denial, not cross-bucket denial; a second bucket-scoped credential/known alternate R2 bucket is still needed for that separate control.


### Latest verified checkpoint — 8 November 2026, 16:51 UTC
- Branch head d66cca79bb12221de7228ffc8b49e4b5167f6f66; PR #1 open/draft/unmerged; main untouched.
- Push CI 42501847900 and PR CI 42501852204 passed all jobs. Live read-only staging browser run 42501847936 passed 10/10, including owner-gated QA/storage routes returning 401 to anonymous callers and student registration remaining disabled.
- Render app deployment dep-dboaenuc6qcc73d3lc00 is live on application commit a9b7bacd4c3069651319df79ce95ec932a7797fc. Auto-deploy remains disabled.
- Staging-only owner controls are enabled at /admin/operations: “Run private storage acceptance” and “Send synthetic QA invitation”. Neither has been clicked yet. The first runs synthetic audio/R2 upload, retrieval, checksum, unsigned-denial and deletion from Render. The second sends a short-lived synthetic QA invitation to the configured owner mailbox; email failure revokes the pending account. Public registration remains disabled.
- No student rows or synthetic QA accounts exist. Neon staging counts: 0 students, 0 synthetic, 1 active admin, 0 approved curriculum sources, 0 topics. Migration 021 is applied.
- Cloudflare inventory has one R2 bucket only; r2.dev is disabled. Neon audio and export buckets are private. Cross-bucket denial is still untested because there is no second R2 bucket/credential.
- Remaining human/operational gates: actual SMTP delivery and account recovery, owner-triggered storage probe, verified synthetic QA invitation and live authenticated browser acceptance, Paystack sandbox, approved curriculum/teacher review, safeguarding/guardian consent/NDPA/DPIA, Nigerian legal review, managed restore, alert delivery, second admin and independent security review.



### Latest verified staging checkpoint — 8 November 2026, 16:55 UTC
- Current Render staging deployment: `dep-dboaidjrjlhs73asffug`, live on `d803ece32de57bbffd3ede3ad48b52e951ab7e64`. The service is Free and auto-deploy remains disabled.
- Staging environment now explicitly sets `APP_ENV=staging`, `STUDENT_REGISTRATION_ENABLED=false`, `STAGING_STORAGE_DIAGNOSTICS_ENABLED=true`, and `STAGING_QA_IDENTITY_ENABLED=true`; `STAGING_QA_EMAIL` is set to the confirmed owner mailbox. These settings only enable owner-triggered staging diagnostics; they do not create accounts or enable public registration.
- Live read-only browser workflow [42501984433](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42501984433) passed after the flags were enabled, including anonymous denial on the synthetic QA and storage diagnostic endpoints. CI push/PR [42502089029](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42502089029) and [42502095096](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42502095096) passed all jobs.
- Neon staging: 21 migrations through 021; 0 students; 0 synthetic QA identities; 1 active owner; 0 consent records. Neon audio and export QA prefixes are empty. No real learner data was created or changed.
- Next unavoidable owner action: sign in at `https://learnwise-staging-api.onrender.com/admin/operations`. Click **Run private storage acceptance** to execute the R2 and Neon audio PUT/GET/SHA-256/unsigned-denial/DELETE probes from Render's runtime. Then use **Send test email to my admin address**; if it succeeds, click **Send synthetic QA invitation**, verify the email link, and sign in to complete authenticated live browser acceptance. Do not share the password or verification link in chat.
- Storage diagnostics and QA invitation are owner-only, CSRF-protected, staging-only and audited. QA identity expires within 24 hours and is blocked from all learner data/learning routes. SMTP failure revokes the pending QA identity. The storage diagnostic can be retried after 15 minutes.
- Still blocked on actual owner execution: storage data-plane acceptance, SMTP delivery, synthetic account verification and authenticated live browser acceptance. All other human/provider dependencies remain as listed in the release gate register.


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


---

## Execution continuation — 8 November 2026, 18:50 WAT

Read-only verification was repeated against the current development branch and staging infrastructure before this addendum.

- Branch head at verification: `112f15f764299639763471f7813aea776a334358`; exact-head workflow `42505261079` passed API/security + PostgreSQL lifecycle/restore tests, non-publishing container build, and staging health. The health job explicitly recorded HTTP 200, JSON status `ok`, mode `database`, service `secondary-school-api`.
- Live read-only staging browser run `42505118340` passed 10/10 after the latest staging safety deployment. This remains anonymous/read-only acceptance; it is not authenticated live-student acceptance.
- Render `learnwise-staging-api` is live at deployment `dep-dbob0qh5efls73dc3tg0` on commit `97f243d3a1daea2ad910f59c405066ab75484955`. The branch is seven commits ahead; the compare contains documentation and browser-test-spec changes only, with no application runtime files. Auto-deploy remains disabled.
- Neon `think-tank-staging` is ready with 21 migration records through 021; the 021 source blob hash matches the current branch migration file. Read-only counts: zero students, one active administrator, six subjects, zero topics, zero curriculum source records.
- Both private Neon buckets are empty. The existing Neon storage credential is branch-scoped, not bucket-scoped. No managed snapshots are listed; the backup branch exists but no managed restore drill has passed.
- R2 control-plane object acceptance and anonymous HTTP 401 denial have previously passed. Render-runtime S3 acceptance and Neon audio data-plane acceptance remain outstanding.
- SMTP diagnostic previously returned `smtp_diagnostic_unavailable` (503); provider details are redacted in logs. No verified delivery or account recovery is established. Synthetic QA issuance remains disabled and no synthetic account exists.
- Remaining human/provider gates are Paystack sandbox E2E, licensed curriculum and teacher approvals, safeguarding/guardian consent/NDPA/DPIA/legal review, managed recovery, monitoring alert delivery, second administrator and independent security review.

No secrets were read or changed. No database writes, student creation, storage object creation, payment, PR merge, main-branch change, production deployment, paid upgrade or destructive action was performed during this verification.



---

## Follow-on execution — provider and authenticated acceptance attempt, 8 November 2026

Current development branch head after the status/handover documentation commits: `5a80d067e16b20f5c9fad0451f17d929398d546d`. The latest Render application deployment remains `dep-dbob0qh5efls73dc3tg0`, live on `97f243d3a1daea2ad910f59c405066ab75484955`. The application file `secondary-school-platform/backend/app.py` has the same Git blob SHA at the deployed commit and current development head, so the owner-only diagnostic routes are the same source version. No new application deployment was necessary.

### SMTP investigation
- Queried Render application logs for SMTP diagnostic attempts. Three warnings were returned at 11:02:12Z, 11:02:17Z and 11:02:26Z; the messages deliberately suppress provider details. No successful SMTP submission or delivery evidence exists.
- Inspected the SMTP implementation: it requires `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, optional `SMTP_PORT` (587 STARTTLS or 465 SSL), and a valid `SMTP_FROM` (defaults to SMTP_USERNAME). Identity links additionally require an HTTPS `PUBLIC_APP_URL`.
- The application source records a bounded phase and exception class in its diagnostic failure log/audit; neither Render's secret values nor provider credentials are exposed to this workflow. The existing diagnostic is owner-authenticated and sends only to the signed-in administrator's own address.
- No secret values were read, overwritten or rotated. SMTP remains blocked until the owner runs the diagnostic from the authenticated admin session and verifies receipt in the mailbox. If it fails again, inspect the redacted failure phase/class and verify the Brevo SMTP login (not API key), sender verification, host, port/TLS mode and account status in Brevo/Render.

### Private storage and synthetic identity
- Read the current `storage_acceptance.py` implementation. Its owner-only staging probe creates a synthetic WAV and independently tests the private Neon audio bucket and Cloudflare R2 export bucket: PUT, GET, SHA-256, unsigned access denial and DELETE/absence verification. It does not use learner data.
- Queried Render logs for storage acceptance; no storage-probe execution logs were found in the available window. The diagnostic has not been shown to pass.
- The endpoint requires an authenticated administrator session with `settings.manage`, valid CSRF, staging environment and the explicit feature flag. The connected Render/GitHub/Neon tools do not provide access to the user's browser session or an in-container command facility; therefore this workflow cannot impersonate the administrator or invoke the owner-only POST safely. No object was created in this follow-on.
- Synthetic QA issuance is similarly owner-only and must send a verified mailbox invitation. No synthetic identity was issued and no authenticated live-student session was created. Public registration remains disabled.

### External release gates
No external credentials, provider transactions, licensed source material, legal opinions, guardian consents, named safeguarding appointment, second administrator, recovery objective or on-call contact can be fabricated or inferred. The remaining gates must be completed with the appropriate provider/authority and recorded evidence. Keep production, live payment, public registration and export worker disabled.

### Exact execution boundary
No Render environment variables were changed; no deploy, migration, database write, bucket mutation, payment, email send, QA-account creation, PR merge, main-branch change or production action was performed in this follow-on. This is an evidence-gathering checkpoint, not a claim that SMTP, storage or authenticated acceptance passed.


## Authoritative follow-on — Brevo HTTPS migration and storage diagnostics (8 November 2026, 22:48 UTC)

This section supersedes earlier SMTP-specific remediation instructions above. Do not restore SMTP delivery or ask for SMTP host/user/password. The staging application now uses the Brevo transactional HTTPS API.

### Verified implementation and deployment
- `backend/identity_email.py` sends transactional messages to Brevo `POST https://api.brevo.com/v3/smtp/email` using the `api-key` header and JSON `sender`, `to`, `subject`, and `textContent`.
- Email verification and password reset retain the existing one-time token purpose, expiry, HTTPS `PUBLIC_APP_URL`, generic response behavior and no-token logging. Synthetic QA invitation remains staging-only, short-lived, isolated and fail-closed; failed email submission or audit triggers account revocation.
- Owner-only diagnostic at the existing `/api/v1/admin/diagnostics/smtp` route is now a Brevo API diagnostic (route path retained for compatibility). It requires staging, explicit diagnostic flag, authenticated admin, CSRF and `settings.manage`; rate limiting and audit remain. A Brevo `messageId` means API acceptance, not proof of mailbox delivery. The admin must confirm actual receipt before QA invitation.
- Exact-code workflow [42531848081](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42531848081) passed all jobs, including unit/security, syntax, disposable migration and backup/restore rehearsals, PostgreSQL integration, synthetic QA lifecycle, assessment/payment/student journey, authenticated disposable browser suite, container build and staging health. Live read-only browser workflow [42531848240](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42531848240) passed. CI authenticated browser tests use disposable fixtures and do not replace live authenticated staging acceptance.
- Render staging deploy `dep-dbofnvajnfac73eor480` is live on application commit `31fdde1e05ef6ab8bb360e86e7df560a21246149`. Render logs show the new container started and service live. This execution network could not independently fetch the post-deploy public health endpoint; do not claim a fresh HTTP 200 without a new verified check.
- Storage acceptance now reports only safe metadata: exception class, bounded provider code, HTTP status, retryability and missing setting names. No provider response body, credential, endpoint, object key or user content is returned.

### Required external configuration — not yet completed
- Add `BREVO_API_KEY` and `BREVO_SENDER_EMAIL` directly in Render Environment. The sender email must already be verified in Brevo. Optional `BREVO_SENDER_NAME=Think Tank`. The API key is not an SMTP key. Do not paste secrets into chat or repository. No Brevo key or sender value has yet been set by this workflow.
- Private audio storage accepts dedicated `AUDIO_STORAGE_ACCESS_KEY_ID`, `AUDIO_STORAGE_SECRET_ACCESS_KEY`, `AUDIO_STORAGE_ENDPOINT_URL_S3`, `AUDIO_STORAGE_REGION`, `AUDIO_STORAGE_BUCKET`, with backward-compatible `AWS_*` fallbacks.
- R2 exports accept canonical `DATA_EXPORT_AWS_ACCESS_KEY_ID`, `DATA_EXPORT_AWS_SECRET_ACCESS_KEY`, `DATA_EXPORT_AWS_ENDPOINT_URL_S3`, `DATA_EXPORT_AWS_REGION`, `DATA_EXPORT_STORAGE_BUCKET`, or aliases `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, `R2_REGION`, `R2_BUCKET_NAME`. Cloudflare R2 endpoint uses signing region `auto`. R2 credential must have Object Read & Write, scoped only to `think-tank-private-exports`. Keep audio and export buckets/credentials separate. No new token or permissions change has been made; diagnostic must validate actual access.

### Exact next actions and release order
1. Owner adds Brevo API key and verified sender directly in Render Environment; no secrets in chat.
2. Owner signs in at `https://learnwise-staging-api.onrender.com/admin/operations`, runs the email diagnostic and confirms the message actually arrived. Do not issue QA invitation merely because Brevo returned a message ID.
3. Owner runs private storage acceptance from the same authenticated Operations page. Require both audio and R2 to pass upload, retrieval, SHA-256 comparison, unsigned access denial, and delete/absence. If failed, use only safe returned provider code/status and missing setting names to correct configuration and permissions, then rerun.
4. Only after actual email receipt and both storage probes pass, temporarily enable the staging-only synthetic QA identity issuance flag, send the invitation, verify the mailbox and sign in. Complete authenticated live-staging acceptance using the synthetic identity only; then revoke/expire it and disable issuance.
5. Keep public registration, live payments, export worker, production deployment, PR merge and `main` changes disabled unless separately approved.

The owner-only operations require a live administrator browser session and CSRF. The connected GitHub/Render/Neon tools do not expose that session. Do not bypass auth, forge cookies, issue QA identities directly in SQL, or fabricate a test pass. Stop only at the real owner/credential gate; continue all read-only checks and safe branch work independently.


---

# Execution checkpoint — 9 November 2026 (live deployment reconciliation)

## Exact verified state
- Current development branch head before this documentation checkpoint: `47b5207319b46410cdbbda0c41a3bc4116871518`.
- PR #1 is open, draft and unmerged. Main remains at `5d6d93ceec31ff3eb6851d567e4d61f7477bc492`.
- Exact-head PR CI run [42532066949](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42532066949) completed successfully: API tests, container build and staging-health jobs all passed.
- Live read-only browser run [42532062468](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42532062468) passed. It is anonymous/read-only staging acceptance, not authenticated QA-user acceptance.
- Render workspace: Emmanuel's workspace, ID `tea-da2svh0ae00c73cs4qq0`. Service `learnwise-staging-api`, ID `srv-dbkqcmt9fdbs73c2kdpg`, Free plan, Frankfurt, Docker, auto-deploy off.
- Latest Render deploy `dep-dbofnvajnfac73eor480` is live on application commit `31fdde1e05ef6ab8bb360e86e7df560a21246149`.
- GitHub compare from deployed application commit to branch head shows only two documentation files changed: `secondary-school-platform/MASTER_CONTINUATION_PROMPT.md` and `secondary-school-platform/STATUS.md`. No runtime code change is pending deployment; do not trigger a redundant redeploy for documentation-only commits.
- Neon staging project `spring-cloud-84267029`, branch `br-still-cherry-baz7g5hk`, state Ready. Read-only counts: 0 students, 1 active administrator, 6 subjects, 0 topics, 0 curriculum source records, 21 migrations (001–021).
- Neon lists private buckets `learnwise-private-audio` and `think-tank-private-exports`; audio bucket object list is empty. No managed Neon snapshots exist and the snapshot schedule is empty.

## Brevo and storage: critical configuration distinction
- Current deployed `backend/identity_email.py` sends mail using Brevo HTTPS API, not SMTP. It requires `BREVO_API_KEY` and `BREVO_SENDER_EMAIL`; optional `BREVO_SENDER_NAME`; `PUBLIC_APP_URL` must be the HTTPS staging origin. Old SMTP variables/SMTP key do not satisfy these requirements. Sender identity must be verified in Brevo.
- Render integration does not expose an environment-variable read/list action. Never claim secret variables are present or absent based on a connector read; the current owner-reported values are not independently inspectable here. Never ask the owner to paste secrets into chat.
- Owner must add Brevo API key and verified sender directly in Render Environment. Then owner signs in at `https://learnwise-staging-api.onrender.com/admin/operations`, runs the email diagnostic and confirms actual receipt in the controlled mailbox. A Brevo API message ID alone is not proof of mailbox receipt.
- Owner must also run the private storage acceptance control from the same authenticated Operations page. Require PASS for both audio and R2: PUT, GET, SHA-256 match, unsigned-access denial, deletion and confirmed absence. Use only safe bounded diagnostic output to troubleshoot.
- Do not issue the synthetic QA invitation until actual Brevo mailbox receipt and both private storage probes pass. Keep public registration disabled.

## Next operator actions
1. Wait for owner to add `BREVO_API_KEY` and `BREVO_SENDER_EMAIL` directly in Render; do not request their values.
2. Have owner run the owner-only email diagnostic and confirm mailbox receipt.
3. Have owner run private audio + R2 storage acceptance and provide only the non-secret results.
4. If both pass, proceed with short-lived synthetic QA invitation, authenticated live staging acceptance, then revoke/expire the identity and disable QA issuance.
5. Continue Paystack sandbox, curriculum rights/teacher approval, privacy/safeguarding/legal approvals, managed recovery, monitoring/alerts, second administrator and independent security review.
6. Re-fetch branch, PR, CI, Render deploy and Neon state before every mutation. Do not redeploy unless runtime code changes and exact-head CI passes.
7. Update both `STATUS.md` and this master prompt after each meaningful milestone.

## Release posture
**NOT READY** for public onboarding or production. No live payment, public registration, production deploy, paid upgrade, destructive database action, PR merge or main-branch modification was performed in this checkpoint. Keep PR #1 open/draft/unmerged and main untouched.



## Brevo diagnostic hardening — 9 November 2026

- Updated `backend/identity_email.py` to raise typed, safe diagnostic failures. Provider HTTP failures now retain the numeric HTTP status and only a bounded machine-readable Brevo `code` token; provider `message` and response body are never exposed. Network failures report `connection_error` without a fabricated status. Missing/invalid configuration reports only the setting name and a bounded category.
- Updated the owner-only Brevo diagnostic endpoint to return a `diagnostic` object containing phase, failure category, HTTP status, provider error code, and (only when applicable) missing setting. The same bounded metadata is audit-logged. API keys, sender/recipient addresses, provider messages, response bodies, endpoints and message content are not included.
- Added focused tests for HTTP 401, HTTP 400, malicious provider-code rejection, missing API key, connection failure, and redaction of private provider messages. Existing successful-send and identity-link tests remain.
- Code commits: `fba9cb98b3d4744f61e61a523b9573d765fd5e8c` (email client), `681c56a564caaf3f013303d745d974ce571b9271` (diagnostic route), `6577e205bd8c90ab0c62bbdacf0563eac4c3168f` (tests).
- **Verification pending:** exact-head CI/test results must be checked before deployment. Render auto-deploy is off; do not redeploy until checks pass and owner approves/required staging change is scheduled. The live diagnostic still requires the authenticated administrator session.
- This change does not send email, read/change secrets, or alter staging configuration. PR #1 remains draft/unmerged; `main` remains untouched. Public registration, live payments and production deployment remain disabled.


## Brevo failure diagnostics deployed end-to-end — 9 November 2026, 17:16 UTC

### Verified implementation and deployment
- Development branch head deployed to staging: `7986b4a4cff506bc1d7aef4e39bb67a27e460330`.
- Render deployment `dep-dbovv70u01pc73frqpag` is **live** on that exact commit. Service auto-deploy remains OFF; this was a one-off manual staging deploy after CI passed. No auto-deploy setting change was made.
- Exact-head CI run [42662442228](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42662442228) completed successfully. API/security + PostgreSQL lifecycle/restore + authenticated browser acceptance, container build and live staging-health checks all passed.
- Live read-only browser acceptance [42662430725](https://github.com/JephterAce/Year-1-Tutorial/actions/runs/42662430725) passed on the same commit.
- Backend now returns only bounded safe diagnostic metadata: phase, failure category, numeric HTTP status, validated Brevo machine code, and missing setting name when applicable. It never returns/logs the API key, sender/recipient, provider message/body, endpoint or message content.
- Admin Operations now preserves the error payload and displays only those approved fields in a preformatted output. A browser regression test simulates a Brevo HTTP 401 with provider code `unauthorized` and confirms the owner sees both values.

### What the available evidence says about the actual email failure
- The last historic Render application failure before this code was deployed was 8 November 2026 at 23:24 UTC. It recorded phase `brevo_api_submission` and exception class `RuntimeError`, but did not retain an HTTP status or provider code. That old record cannot distinguish a missing/invalid setting, rejected API key/sender, provider validation error or network problem.
- The separate historic SMTP timeout is from the legacy SMTP path and is not proof that the current Brevo HTTPS API has the same failure.
- **The underlying provider cause is still unconfirmed.** Render's connected tools do not expose secret environment-variable values and cannot act inside the owner's authenticated browser session/CSRF context. Do not guess or rotate credentials without the new diagnostic evidence.

### One required owner action — run once, then share only safe output
1. Open [Think Tank Operations](https://learnwise-staging-api.onrender.com/admin/operations) and sign in as the owner.
2. Under **Staging email delivery test**, click **Send test email to my admin address** once.
3. Copy only the displayed `diagnostic` object (phase, failure_category, http_status, provider_error_code, missing_setting) into the continuation chat. Never share API keys, passwords, sender/recipient addresses, cookies or screenshots that reveal secrets.
4. If the request is accepted, confirm whether the message actually arrived. A Brevo `messageId` / HTTP acceptance is not proof of inbox delivery.

Do not run a second test until the first safe result has been interpreted. Do not create another key unless the returned status/code shows that key replacement is warranted. Keep public registration, live payments, synthetic QA issuance and production deployment gated. PR #1 remains draft/open/unmerged; `main` is untouched. No credentials were read or changed by this work.


## Continuation instructions after diagnostic deployment

Resume by first reading the latest `STATUS.md` section above and checking Render deploy/branch/CI state. The diagnostic hardening is already live on staging at commit `7986b4a4cff506bc1d7aef4e39bb67a27e460330`; do not repeat the code or UI changes. The next dependency is the owner's single authenticated run from `/admin/operations`. Ask for only the displayed safe diagnostic object and interpret the actual fields before recommending any configuration change. Do not ask for, read, or store provider secrets. Auto-deploy remains deliberately off; use a manual staging deploy only after exact-head CI passes. Keep PR #1 draft/unmerged and `main` untouched. No production deployment, live payments, public registration or synthetic QA issuance is approved.
