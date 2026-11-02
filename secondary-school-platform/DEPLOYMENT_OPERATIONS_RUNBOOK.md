# Hosting and operational runbook

## Current posture
The repository includes a non-root Gunicorn container and a disposable PostgreSQL rehearsal environment. These are deployment foundations, not a production deployment. No hosting provider, cloud account, domain or production secret has been authorised.

## Required infrastructure
- Managed PostgreSQL with TLS, encrypted backups and point-in-time recovery.
- Application container behind HTTPS reverse proxy/WAF; private object storage for audio.
- Separate migration and least-privilege runtime database identities.
- Secret manager for DB URL, session/rate-limit peppers, email, Paystack and audio signing keys.
- Separate staging and production environments; immutable image digest and manual production approval.
- Centralised structured logs, error monitoring, uptime checks, alert routing and audit retention.

## Release sequence
1. Build and scan image; pin base image and dependencies.
2. Deploy staging with synthetic accounts and sandbox payment provider.
3. Restore a backup into an isolated rehearsal environment.
4. Apply pending migrations using a dedicated migration role; verify checksums/schema.
5. Run API, browser, webhook replay, audio entitlement and accessibility tests.
6. Verify restore, rollback/forward-fix plan, alert delivery and incident contacts.
7. Obtain product, security, safeguarding, privacy/legal and finance approval.
8. Deploy immutable image to production with human approval.
9. Smoke-test health, login, catalogue, assessment and payment mode.
10. Monitor errors, latency, DB saturation, failed jobs, outbox age, webhook failures and admin access.

## Alerts
Health/readiness failures; sustained 5xx; login abuse; admin auth failures; DB saturation/backup failures; payment verification/fulfilment failures; notification outbox backlog; assessment submission failures; review queue age; audio token denials and object-store errors.

## Stop conditions
Do not deploy if migrations are unreviewed, secrets missing, backups unverified, privacy/safeguarding sign-off absent, sandbox payment tests fail, or critical/high security findings remain open.
