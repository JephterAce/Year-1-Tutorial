# Learnwise backend

Isolated Flask/PostgreSQL API for the SS1–SS3 learning platform. The existing Year 1 Telegram bot is outside this application.

## Local development

```bash
cd secondary-school-platform/backend
python -m venv .venv
# Activate the virtual environment
pip install -r requirements.txt
python -m unittest -v
python app.py
```

- Health: `GET /health`
- Catalogue: `GET /api/v1/catalogue`
- Student account: `/api/v1/auth/*`
- Assessment execution: `/api/v1/assessments/{assessment_id}/attempts` and `/api/v1/assessment-attempts/{attempt_id}/*`
- Paystack callback: `POST /api/v1/webhooks/paystack` (development foundation only)

Without `DATABASE_URL`, only the clearly labelled demo catalogue is available. Identity, assessment and payment operations require PostgreSQL and fail closed without it. Use a dedicated TLS PostgreSQL database and never commit real environment files or credentials.

## Ordered database setup

1. Apply `../DATABASE_SCHEMA.sql` using a migration-owner role.
2. Apply migrations `001_platform_hardening.sql` through `008_assessment_immutability.sql` in numeric order.
3. Rehearse on a disposable database, inspect constraints/indexes, and verify rollback/restore before any production migration.
4. Run the application with a least-privilege database role.

No migration has been applied to a live database.

## Student identity

Registration requires explicit Terms and Privacy acceptance. The API supports email verification, login/logout, session revocation, CSRF validation and password reset. The account page assumes a same-origin API or reviewed same-origin reverse proxy. Production requires HTTPS, reviewed origin/CSRF policy, proxy-aware rate limiting, email resend/abuse controls, transactional email outbox and a real PostgreSQL/SMTP end-to-end test.

## Assessment execution

The attempt service creates a briefing-state attempt, checks class eligibility/attempt limits/allowed question counts, and starts only after affirmative agreement to the current briefing policy version. Start populates immutable per-attempt question and answer-key snapshots. Student projections omit answer keys. Server UTC deadlines enforce the 36-seconds-per-question rule, with the 10-question/7-minute exception. Answers are ownership-checked and saved server-side. Submission/expiry grades supported objective types and persists results. Focus/visibility/fullscreen incidents are debounced; the first two warn and the third terminates with an integrity-review flag, not a finding of misconduct.

The browser countdown is display-only. A production client must autosave answers, send integrity events, keep the server deadline visible, and submit persisted answers on expiry. This increment has unit/contract coverage but has not been exercised against PostgreSQL. It does not yet provide an appeal workflow, fault-reporting workflow, robust recovery for concurrent/retried requests, result notifications, admin assessment authoring, or end-to-end browser tests. No essays, handwriting, proofs, webcam or microphone surveillance are supported.

## Payment and owner email

The callback validates the raw Paystack HMAC signature, looks up a server-created pending order, verifies the transaction directly with Paystack, and atomically records payment/entitlement/outbox state. The outbox worker supports leased claims and retries but is not scheduled or monitored. Trusted order creation is not implemented; therefore there is no safe checkout path and real payments must remain disabled. SMTP notification recipient defaults to `emmanuelbjephter@gmail.com`; configure SMTP and Paystack credentials only in the host's secret manager, never in source control or chat. No live email or payment has been tested.

## Release gates

- Dedicated PostgreSQL provisioned; migrations 001–008 rehearsed and applied only after approval.
- SMTP and HTTPS public app URL configured privately; email delivery/resend and operational monitoring tested.
- Payment order creation, reconciliation/refunds, outbox scheduling and alerting implemented before live checkout.
- Verified NERDC/school curriculum source documents supplied; no invented topic/term mapping.
- Nigerian privacy, data-protection, minor-consent, accessibility and safeguarding review completed.
- Security review, production monitoring, backup/restore and incident response tested.

Keep PR #1 draft and unmerged. Do not deploy, apply production migrations, activate live payments, change production secrets/config, spend money, or modify the legacy bot without explicit approval.
