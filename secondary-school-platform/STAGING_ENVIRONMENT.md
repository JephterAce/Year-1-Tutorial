# Think Tank staging environment — 2026-11-03

## Resource map

| Component | Provider | Resource | Plan / location |
|---|---|---|---|
| PostgreSQL | Neon | `think_tank` / `think_tank-staging-rehearsal` | Free, PostgreSQL 16, AWS Frankfurt |
| Private audio | Neon Object Storage | `think_tank-private-audio` | Private bucket on staging branch |
| API + student/admin pages | Render | `think_tank-staging-api` | Free, Docker, Frankfurt |
| Transactional email | Brevo (selected) | Not yet provisioned | Free plan intended; 300/day |
| Payments | Paystack | Existing integration code | Sandbox not yet credentialed |
| DNS/edge | Cloudflare | Connected account | Not required for the current staging URL |

## Staging URLs

- Application/API: https://think_tank-staging-api.onrender.com
- Student home: https://think_tank-staging-api.onrender.com/
- Account: https://think_tank-staging-api.onrender.com/account
- Assessment: https://think_tank-staging-api.onrender.com/assessment
- Lesson: https://think_tank-staging-api.onrender.com/lesson
- Admin operations: https://think_tank-staging-api.onrender.com/admin/operations
- Assessment reviews: https://think_tank-staging-api.onrender.com/admin/reviews
- Health: https://think_tank-staging-api.onrender.com/health

Admin routes return a noindex header and do not expose private data without an authenticated administrator session.

## Database

- Neon project ID: `spring-cloud-84267029`
- Staging branch ID: `br-still-cherry-baz7g5hk`
- Database: `think_tank`
- PostgreSQL: 16
- Migration baseline: `DATABASE_SCHEMA.sql` followed by `backend/migrations/001`–`013`.
- Applied versions are recorded in `think_tank_migration_history`.
- App database role: `think_tank_app`; separate from `think_tank_owner`. The app role is not a superuser and cannot create databases or roles. It cannot update/delete audit events or change administrator roles.
- Do not point Render at the Neon project default branch; keep staging isolated on the named rehearsal branch.
- Do not paste connection strings or credentials into Git, tickets, or ChatGPT messages.

## Private audio

- Bucket: `think_tank-private-audio`
- Access: private; no public bucket policy.
- S3 endpoint and branch-scoped access credentials are injected into Render's secret environment.
- Backend supports upload to pending review, reviewer approval/rejection and authenticated same-origin streaming with byte-range forwarding.
- Uploaded files are limited to 100 MB and checked against allowed MIME types and file signatures.
- No approved audio assets exist yet. Malware scanning and a real approved content corpus remain additional release requirements.

## Brevo email setup still required

Render has non-secret configuration for:
- `PUBLIC_APP_URL=https://think_tank-staging-api.onrender.com`
- `SMTP_HOST=smtp-relay.brevo.com`
- `SMTP_PORT=587`

Still required in Brevo and Render:
- Verify a sender/domain in Brevo.
- Add `SMTP_USERNAME` and `SMTP_PASSWORD` as Render secret environment variables.
- Set `SMTP_FROM` to the verified sender.
- Test verification and password-reset emails using a controlled mailbox.
No SMTP credentials are stored in the repository.

## Staging safety flags

- `STUDENT_REGISTRATION_ENABLED=0` — public student signup is disabled until Brevo delivery and safeguarding/privacy checks are verified.
- `PAYMENTS_ENABLED=0` — checkout is disabled until Paystack sandbox testing is completed and reviewed.

These flags are set in Render's environment. Do not enable them for real users until the corresponding release gates are signed off.

## First administrator

There is no public administrator sign-up. Use `backend/bootstrap_admin.py` once from a trusted environment after setting:
- `DATABASE_URL` to the staging database (never paste it into chat).
- `THINK_TANK_ADMIN_EMAIL`.
- `THINK_TANK_ADMIN_PASSWORD` (strong unique password).
- `THINK_TANK_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN`.

The script refuses to overwrite an existing account, hashes the password with scrypt and writes an audit event. Remove bootstrap environment variables after success. Do not create an admin account until the owner chooses the intended administrator email.

## Cost guardrails

- Keep Render on Free for staging. It may sleep when idle and has no production uptime guarantee.
- Keep Neon at 0.25 CU and monitor the Free plan's 100 CU-hours/month and 1 GB database storage allowance. Neon Free also includes 5 GB object storage.
- Keep all audio private and within the Neon storage allowance. Consider Cloudflare R2 only if storage grows; its current Free allowance is 10 GB-month standard storage, 1M Class A and 10M Class B requests, with no egress charge. Activating R2 requires a separate subscription checkout.
- Brevo Free provides 300 sends/day and transactional email. Upgrade only if actual sending volume or deliverability requirements justify it.
- Paystack has no integration fee; transaction fees apply when a payment succeeds. Keep all testing in sandbox until the owner approves live activation.

## Safety

This is an isolated staging environment using synthetic data only. It is not approved for real students. No production deployment, live payment, public audio, or public student registration should be enabled before the external release gates in `RELEASE_GATE_REGISTER.md` are closed.
