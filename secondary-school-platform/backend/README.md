# API foundation

Local Flask API for the separate senior-secondary learning platform.

## Local run
```bash
cd secondary-school-platform/backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
python -m unittest -v
python app.py
```

Health endpoint: `GET /health`
Catalogue endpoint: `GET /api/v1/catalogue`
Optional filters: `?class=SS2&subject=general-mathematics&term=1&q=quadratic`

## Demo and database modes
Without `DATABASE_URL`, the API returns clearly labelled illustrative demo catalogue records. With `DATABASE_URL`, it queries published topics from the dedicated platform database. It does not silently fall back to sample records when a configured database is unavailable.

Copy `.env.example` to a local `.env` and set a dedicated PostgreSQL connection string. Never commit the real `.env` or share database credentials in chat.

## Database setup
1. Provision a separate PostgreSQL database for this platform; do not reuse the Year 1 bot's SQLite database.
2. Apply `../DATABASE_SCHEMA.sql` using a database owner/migration role.
3. Apply `migrations/001_platform_hardening.sql`.
4. Apply `migrations/002_identity_security.sql`.
5. Apply `migrations/003_nerdc_curriculum_metadata.sql`.
6. Apply `migrations/004_student_profiles_and_assessments.sql`.
7. Apply `migrations/005_student_data_exports.sql`.
8. Apply `migrations/006_payment_notification_outbox.sql`.
9. Configure the application connection using a least-privilege database role and TLS.
10. Populate approved subjects, terms and curriculum-reviewed topics before expecting the production catalogue to show results.

## Current security boundary
This API currently exposes health and a public list of published catalogue topics only. It does not yet provide student registration/login, admin authorisation, payment processing, webhook handling, entitlement checks, or protected audio delivery. Do not add secrets to source control or connect live payments until these controls and their tests are implemented.

## Payment email alerts (foundation only)
The backend includes `payment_notifications.py`, which sends a minimal owner notification to `PAYMENT_ALERT_RECIPIENT` (default: `emmanuelbjephter@gmail.com`) through a configured SMTP relay using TLS. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` and optionally `SMTP_FROM` as deployment secrets. Do not commit credentials or paste them into chat.

This mailer is deliberately not connected to a public checkout redirect. A future Paystack webhook handler must first verify the webhook signature, fetch/verify the transaction server-side, confirm amount/currency/reference and idempotently record the successful payment, then enqueue the alert. A mail failure must not reverse a valid payment or duplicate fulfilment; use a durable retry/outbox worker. Live payment/webhook processing and SMTP delivery are not enabled yet.


## Paystack webhook security primitives (not a live integration)
`paystack_webhooks.py` verifies the HMAC-SHA512 signature against the exact raw request body and validates the minimum shape of a `charge.success` event. Its tests use synthetic payloads only.

This helper is not a payment endpoint and must not grant access or trigger email. Before fulfilment, the future service must fetch the transaction from Paystack using a server-held secret, compare the verified reference/amount/currency against a pending server-created order, atomically record the payment and entitlement with unique idempotency constraints, and enqueue an owner email in a durable outbox. Do not trust the webhook payload alone. No Paystack secret, checkout, live webhook route, entitlement grant or live email is configured.


## Paystack callback and verified fulfilment (development only)
The backend now exposes `POST /api/v1/webhooks/paystack`. It authenticates the exact raw request body using `x-paystack-signature`, requires a matching server-created `payment_transactions` order, fetches the transaction from Paystack's verification API, compares reference/amount/NGN currency/status, and atomically records payment success, entitlement and an owner-email outbox row. Duplicate callbacks use deterministic idempotency keys. A processing/database failure returns a retryable 503; an invalid signature returns 400.

The outbox is durable, but an email delivery worker and retry/dead-letter scheduler are not yet implemented. Therefore this callback queues an alert but does not send one. Do not configure live Paystack callbacks or accept real payments until student authentication, trusted order creation, operational monitoring, outbox worker/retries and deployment controls are complete. The migration must be applied only to a dedicated Learnwise database after migrations 001–005.


## Payment email outbox worker
`payment_outbox.py` provides a single-item worker function for a supervised scheduler/background process. It claims rows using PostgreSQL `FOR UPDATE SKIP LOCKED`, reclaims stale processing leases, sends through the configured TLS SMTP adapter, marks successful delivery, and retries failures with capped exponential backoff (30 seconds up to 1 hour; 8 attempts before dead-letter). It never runs inside the webhook request. The host must schedule this worker and monitor dead-letter rows before live payment activation.
