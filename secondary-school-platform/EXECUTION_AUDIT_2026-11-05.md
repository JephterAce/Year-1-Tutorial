# Think Tank execution audit — 5 November 2026

## Scope and safety
This is a read-only provider audit plus a repository handover record. It does not change production, apply migrations, alter secrets, create administrator/student accounts, deploy code, enable payments, publish curriculum, or modify the legacy university Telegram bot.

Think Tank remains an isolated SS1–SS3 learning platform for English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics. The existing Year 1 Telegram university subscription product is separate. The intended student-facing Telegram integration is a broadcast-only Think Tank Channel; no student bot or group is in scope.

## Verified GitHub state
- Repository: `JephterAce/Year-1-Tutorial`; default branch: `main`.
- Development branch: `secondary-school-platform-foundation`.
- Development branch head at audit: `56c5e897bed1920cf9162ee7a54ee75e7b2d56be`.
- PR #1 is open, draft, mergeable and unmerged: https://github.com/JephterAce/Year-1-Tutorial/pull/1
- Latest verified CI run on that exact development head: run 41646320293, completed successfully: https://github.com/JephterAce/Year-1-Tutorial/actions/runs/41646320293
- Both jobs passed: API tests (unit/security, JavaScript syntax, disposable PostgreSQL migration rehearsal, schema integration, assessment/payment DB integration) and container build without publishing.
- The development branch is 33 commits ahead of the currently deployed Render commit `fe9ff76f7b3b53331bfd4179062d7d38ac273d23`.
- Render auto-deploy is disabled. CI success is not evidence that the latest code is deployed or that live browser/provider workflows pass.
- The current `main` branch has two commits beyond the common base. The two affected files were compared and have identical blob content on `main` and the development branch. No merge or sync was performed. Keep PR #1 draft and unmerged.

## Verified Render staging state
- Workspace: Emmanuel's workspace.
- Service: `learnwise-staging-api`; ID `srv-dbkqcmt9fdbs73c2kdpg`.
- URL: https://learnwise-staging-api.onrender.com
- Dashboard: https://dashboard.render.com/web/srv-dbkqcmt9fdbs73c2kdpg
- Free plan, Frankfurt, Docker context `secondary-school-platform`, Dockerfile `secondary-school-platform/backend/Dockerfile`, one instance.
- Auto-deploy: off. Current live deployment: `dep-dbkqu9e7bikc73flcu3g`, commit `fe9ff76f7b3b53331bfd4179062d7d38ac273d23`.
- Render health-check path is blank. The app implements `GET /health`; the runbook says not to configure Render's health-check path until the manual staging browser check passes repeatedly.
- No error or request logs were returned by the provider query for the available seven-day window. This is not a substitute for a successful HTTP/browser health check.
- Environment values were not read. A trusted operator must privately verify that the Render `DATABASE_URL` points to the Neon staging branch/database and uses `learnwise_app`, and confirm the S3 endpoint/region/bucket settings and presence of credentials. Never place secrets in this file, chat, screenshots or source control.

## Verified Neon staging state
- Project: `learnwise`, ID `spring-cloud-84267029`, PostgreSQL 16, region `aws-eu-central-1`.
- Staging branch: `think-tank-staging`, ID `br-still-cherry-baz7g5hk`, non-primary and Ready. Main branch remains separate.
- Database: `learnwise`; database owner: `learnwise_owner`.
- Actual migration table is `learnwise_migration_history` (not `think_tank_migration_history`). It contains the 13 ordered migrations 001–013 and 13 distinct recorded source hashes.
- Aggregate-only audit: six subject rows; zero topic rows; zero student rows; zero administrator rows; zero audit-event rows.
- Role audit: `learnwise_owner` is not a superuser but has database/role creation privileges and can insert into the admin table. `learnwise_app` is not a superuser, cannot create databases/roles, and cannot insert into `admin_users`. The application role can append audit events as designed. Do not use raw SQL to create an administrator.
- Private audio bucket: `learnwise-private-audio`, access level private. The bucket currently contains zero objects.
- No database migrations, role changes, account creation, object writes or deletions were performed during this audit.

## Administrator bootstrap — ready but not executed
The verified script path is `secondary-school-platform/backend/bootstrap_admin.py`. It requires:
- `LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN`
- `DATABASE_URL` for the verified staging database
- `LEARNWISE_ADMIN_EMAIL`
- `LEARNWISE_ADMIN_PASSWORD`

The script normalises the email, hashes the password with scrypt, acquires a transaction-scoped advisory lock, refuses to create an account if any administrator already exists, creates the first owner record and records `admin.bootstrap.created`. Tests are present in `secondary-school-platform/backend/test_bootstrap_admin.py` and are included in the latest passing CI run.

No admin account has been created. Before execution the owner must choose/confirm the admin login email, generate a unique password (12+ characters) in a password manager, and privately verify the target connection. Run once from an ephemeral trusted environment using the staging owner connection (or reviewed narrowly-scoped bootstrap role); never replace the Render runtime app connection with owner credentials. Remove the temporary bootstrap variables/connection immediately after execution, then verify one administrator and the audit event and test login/CSRF/capabilities.

## Browser acceptance and health
A manual GitHub Actions workflow exists:
- Workflow: `.github/workflows/think-tank-staging-browser.yml`
- Tests: `secondary-school-platform/browser-acceptance/staging.spec.js`
- Default target: existing staging URL.
- Workflow checks health, public student pages, account controls, anonymous auth boundaries, private audio authorization and anonymous admin access.
- The workflow has not yet been run against the live service. It does not test successful login, email delivery, complete assessment flow, approved lesson playback or authenticated admin business actions.
- The connected GitHub read tools do not expose workflow dispatch. An owner/operator must start it from GitHub → Actions → Think Tank staging browser acceptance → Run workflow. Do not configure Render `/health` until this passes repeatedly.

## External and operational release blockers
1. **SMTP:** Brevo sender identity, SMTP credentials and real verification/reset delivery are not verified. Keep registration disabled until email and child/privacy gates are approved.
2. **Paystack:** code and mocked integration tests exist; test keys, webhook secret, sandbox transaction, webhook retry/replay, reconciliation/refund evidence are missing. Keep checkout disabled; never use live keys for staging tests.
3. **Outbox operations:** payment notification outbox code exists but has no scheduled/monitored worker. The current worker exposes a `process_one_outbox_item()` function; no production/staging job was created.
4. **NERDC curriculum:** official NERDC pages link separate SSS1/SSS2/SSS3 portals, but full authorised class/subject materials and reuse permissions are not recorded. All 18 class/subject mappings and teacher sign-offs remain incomplete; the staging catalogue has zero topics. Do not invent topics/terms or scrape/bypass access controls. The six-subject library is not the full 8–9 subject senior-secondary package.
5. **Teachers:** qualified Nigerian subject-teacher review and second review of maths/science accuracy/audio are outstanding.
6. **Privacy/legal/safeguarding:** Nigerian counsel/privacy professional, DPIA, child/guardian consent and age-verification approach, safeguarding lead, data retention/deletion, complaint and incident response approvals remain outstanding. The privacy notice and terms are drafts, not legal clearance.
7. **Audio:** the private bucket is empty; licensed, source-backed scripts, teacher review, audio production/QA and approved lesson assets are not present.
8. **Student/admin functionality:** foundations exist for student identity/profile, objective assessments, result history, assessment issue reporting, admin auth and assessment review. Successful SMTP/browser acceptance, profile-photo workflow, full CMS/curriculum publishing, assessment authoring, complete admin operations/finance and export/deletion UAT remain incomplete.
9. **Telegram:** create/connect only a broadcast-only Think Tank Channel; no bot/group is authorised. The Channel itself has not been verified/connected in this audit.
10. **Operations:** complete backup and timed restore proof, monitoring/alerts, incident/on-call owner, security/accessibility review, staging browser acceptance and tested provider workflows.
11. **Domain:** custom `thinktank.com.ng` is not configured. No purchase or paid upgrade is authorised.

## Current release decision
**NOT READY for public student onboarding or production.** Staging infrastructure and database schema are present; current branch CI is green. The live staging service is behind by 33 commits, browser acceptance has not passed, and third-party credentials, curriculum rights/content, human reviews and legal/safeguarding evidence are missing.

Keep registration and checkout disabled. Do not merge PR #1, deploy the newer branch, change secrets, configure paid services, apply migrations outside disposable CI, create accounts by SQL, publish unverified content, or alter the legacy bot without the required explicit approvals.

## Next owner actions
1. Confirm the exact email address for the first Think Tank owner administrator.
2. In private provider dashboards, verify the staging Render environment targets the Neon staging branch/database and the least-privilege app role; do not disclose values.
3. Run the manual staging browser workflow against the currently deployed service.
4. Run the guarded admin bootstrap privately after target/email/password verification.
5. Supply authorised NERDC material/rights and appoint subject reviewers; arrange Nigerian legal/privacy and safeguarding sign-off.
6. Configure SMTP and Paystack **test** credentials privately, then complete controlled staging tests.
7. Approve a reviewed staging deployment only after the above deployment prerequisites are met.

## Handover rule
Continue on `secondary-school-platform-foundation`. Re-check branch head, CI and Render deployed SHA at the beginning of every session. Do not treat this audit snapshot as a live guarantee after further commits or provider changes.
