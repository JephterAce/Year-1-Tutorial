# Think Tank — Nigerian Senior Secondary Learning Platform

Think Tank is an independent SS1–SS3 learning platform. It is isolated from the existing Year 1 university Telegram subscription bot.

## Initial product scope
- Classes: SS1, SS2 and SS3.
- Six initial subjects: English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics.
- Lesson formats: teacher-led audio, two-presenter educational podcast, transcripts and practice.
- Student journey: register, verify email, browse approved lessons, purchase, listen, practise, view results and request support.
- Admin journey: authenticate, review assessment issues and appeals, audit decisions. Curriculum/content administration remains a controlled workflow.

The six-subject library is not the complete revised national compulsory subject package. Curriculum version target: NERDC revised SSEC 2025. No topic should be labelled officially aligned until its class, source, rights and teacher review are recorded. Term placement and cohort applicability must not be guessed.

## Key implementation
- API: `backend/app.py` (Flask).
- PostgreSQL schema: `DATABASE_SCHEMA.sql`; ordered migrations: `backend/migrations/`.
- Student pages: `frontend/index.html`, `account.html`, `assessment.html`, `lesson.html`.
- Admin preview: `admin/index.html`; protected review console: `admin/reviews.html`.
- Curriculum import and validation: `backend/curriculum_import.py`, `CURRICULUM_IMPORT_TEMPLATE.csv`.
- NERDC acquisition: `NERDC_ACQUISITION_RUNBOOK.md`, `CURRICULUM_WORKFLOW.md`.
- Privacy/safeguarding/legal review: `PRIVACY_SAFEGUARDING_LEGAL_REVIEW.md`, `PRIVACY_NOTICE_DRAFT.md`, `TERMS_OF_SERVICE_DRAFT.md`.
- Audio: `SECURE_AUDIO_DELIVERY.md`, `CONTENT_PRODUCTION_STANDARD.md`, `backend/audio_media.py`.
- Hosting/operations: `backend/Dockerfile`, `docker-compose.rehearsal.yml`, `POSTGRES_REHEARSAL.md`, `DEPLOYMENT_OPERATIONS_RUNBOOK.md`.

## Local API tests
From this directory:

```sh
python -m pip install -r backend/requirements.txt
cd backend
python -m unittest -v
python check_frontend_scripts.py
```

## Disposable PostgreSQL migration rehearsal
From this directory:

```sh
docker compose -f docker-compose.rehearsal.yml up -d postgres
cd backend
THINK_TANK_REHEARSAL_DATABASE_URL='postgresql://think_tank:rehearsal_only_change_me@localhost:55432/think_tank_rehearsal' python rehearse_migrations.py
DATABASE_URL='postgresql://think_tank:rehearsal_only_change_me@localhost:55432/think_tank_rehearsal' python -m unittest -v test_postgres_schema_integration test_postgres_end_to_end
```

The runner loads the baseline schema, applies numbered migrations in order and records checksums. It refuses remote hosts and default database names. Use only the disposable rehearsal database. GitHub Actions repeats this against PostgreSQL 16 and also runs frontend syntax checks, unit/security tests, database integration/E2E tests and a non-publishing container build.

## Runtime configuration
Copy `.env.example` into a secure local secret store or host secret manager. Never commit real values. Production requires HTTPS, managed PostgreSQL with backups, private media storage, a least-privilege database role, SMTP, Paystack secrets and independent random signing/rate-limit keys.

## Important release limitations
- Full official NERDC material acquisition, licensing and teacher verification remain pending authorised access.
- PostgreSQL migrations have been rehearsed on a disposable database, not applied to production.
- Assessment and payment E2E tests use synthetic fixtures and Paystack-shaped stub responses; no real charge is made.
- Private audio routes currently stream from a private local storage root. A production private object-storage adapter, upload workflow and audio content still need to be delivered.
- Student profile fields and assessment history are API-connected; photo storage and profile-visibility changes are not enabled.
- Admin assessment review is connected; full CMS, curriculum publishing and finance operations are not exposed.
- Draft privacy notice and terms require Nigerian legal review, a completed DPIA and child-safeguarding approval.
- No hosting provider, domain, production secrets, live payment credentials or production deployment is configured.

## Protect the existing service
All Think Tank work remains under `secondary-school-platform/` and on `secondary-school-platform-foundation`. Do not deploy this product over the legacy service or modify the separate university bot `@Ustpaymentbot`. Keep PR #1 in draft until the owner approves review and release.
