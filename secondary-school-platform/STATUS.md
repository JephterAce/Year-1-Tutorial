# Implementation status

Last updated: 2026-11-01

## Verified present in this development branch
- GitHub write access confirmed; isolated development branch created.
- Product overview, product specification and staged build/release roadmap.
- NERDC curriculum source register, scope definitions and mandatory curriculum/term-allocation validation rules.
- Initial PostgreSQL relational schema plus two follow-up migrations: baseline hardening/webhook event ledger and identity-token/admin credential schema. Migrations are authored but have NOT been applied to a live database.
- Responsive student portal UI prototype at `frontend/index.html`, updated to display all six requested subjects and pending term allocations.
- Admin workspace UI prototype at `admin/index.html`, updated to show the six-subject scope.
- Flask API with health endpoint and catalogue endpoint.
- PostgreSQL repository layer that reads published topics when a dedicated `DATABASE_URL` is configured; otherwise the API explicitly serves demo catalogue data.
- Query filters for class, subject, term and search, with invalid class/term validation.
- Environment-variable example and setup guidance; no real credentials stored in Git.
- API and database-configuration unit tests executed successfully in GitHub Actions (run 41342284699; `api-tests` job completed successfully).
- Git ignore rules for secrets, databases, dependencies and generated media.
- All new work is confined to `secondary-school-platform/` on the development branch.

## Not yet implemented
- Provisioned PostgreSQL database, applied migrations, seeded approved curriculum catalogue or production student records.
- Complete topic-by-topic NERDC capture for all 18 class/subject combinations and school-specific term mapping.
- Student registration/login, email delivery for verification/reset, password reset flows, session revocation endpoints or admin authorisation.
- Paystack checkout, server verification, webhook processing, refunds or entitlement fulfilment.
- Private audio storage, signed media delivery or playback.
- Telegram bot/account linking/notifications.
- AI voice generation, lesson scripts or editorial approval workflow.
- Automated baseline test suite and CI job passed in run 41342284699. The six-subject UI/API changes, curriculum documentation and migrations 002–003 were committed after that run and still need a fresh CI run. Security review, database integration tests, backup/restore and deployment remain outstanding.
- Production domain, privacy/terms/refund policy and support process.

## Safety statement
The student and admin interfaces remain prototypes. The API does not yet handle accounts, payments, real student data or protected audio. No production database has been connected, no migrations have been applied, and no live service or legacy bot has been changed or deployed.
