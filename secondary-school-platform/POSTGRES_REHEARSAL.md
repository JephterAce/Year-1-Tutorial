# PostgreSQL migration rehearsal

## Disposable local database
From the secondary-school-platform directory:

```sh
docker compose -f docker-compose.rehearsal.yml up -d postgres
cd backend
python -m pip install -r requirements.txt
LEARNWISE_REHEARSAL_DATABASE_URL='postgresql://learnwise:rehearsal_only_change_me@localhost:55432/learnwise_rehearsal' python rehearse_migrations.py
```

The runner loads the baseline DATABASE_SCHEMA.sql once, then migrations 001 onward in order. It records SHA-256 checksums and refuses changed historical schema/migrations. Re-running against the same disposable database should apply nothing.

## Safety
- The runner refuses remote database hosts and default database names.
- Use only a disposable database; never point it at production or the legacy university bot database.
- Reset only the disposable rehearsal volume when you intentionally want a clean replay.
- CI runs the unit/security suite and a fresh PostgreSQL 16 replay on every platform change.

## What this proves
A clean baseline plus numbered migration chain can be applied to a fresh PostgreSQL instance. It does not prove production data compatibility, restore safety, load capacity or operational readiness. Those require a sanitised production-like snapshot and an approved rehearsal.
