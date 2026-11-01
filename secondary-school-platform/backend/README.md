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
6. Configure the application connection using a least-privilege database role and TLS.
7. Populate approved subjects, terms and curriculum-reviewed topics before expecting the production catalogue to show results.

## Current security boundary
This API currently exposes health and a public list of published catalogue topics only. It does not yet provide student registration/login, admin authorisation, payment processing, webhook handling, entitlement checks, or protected audio delivery. Do not add secrets to source control or connect live payments until these controls and their tests are implemented.

## Payment email alerts (foundation only)
The backend includes `payment_notifications.py`, which sends a minimal owner notification to `PAYMENT_ALERT_RECIPIENT` (default: `emmanuelbjephter@gmail.com`) through a configured SMTP relay using TLS. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` and optionally `SMTP_FROM` as deployment secrets. Do not commit credentials or paste them into chat.

This mailer is deliberately not connected to a public checkout redirect. A future Paystack webhook handler must first verify the webhook signature, fetch/verify the transaction server-side, confirm amount/currency/reference and idempotently record the successful payment, then enqueue the alert. A mail failure must not reverse a valid payment or duplicate fulfilment; use a durable retry/outbox worker. Live payment/webhook processing and SMTP delivery are not enabled yet.
