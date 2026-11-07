# Migration and main-branch reconciliation

Checked 2026-11-07.

## Main-branch changes preserved

The current `main` head recorded in the earlier reconciliation is `5d6d93ceec31ff3eb6851d567e4d61f7477bc492`, two commits ahead of the PR's previous base `ac472be3e6de796ce5f6c3ea4e5f343dc172cd1d`.

The two intervening main commits add:
- `AUTOMATED_ASSESSMENT_AND_STUDENT_PROFILES.md` — product and acceptance-test specification.
- `migrations/004_student_profiles_and_assessments.sql` — an earlier schema migration.

Both files are retained verbatim on this development branch. Do not apply the root-level historical migration on top of the canonical backend sequence.

## Canonical backend migration sequence

The canonical backend sequence is now `backend/migrations/001` through `backend/migrations/019`, applied after `DATABASE_SCHEMA.sql` as the baseline. The baseline plus 19 numbered migrations gives 20 migration-history entries in the disposable CI rehearsal.

- Migrations 001–013 are present in managed Neon staging.
- Migrations 014–019 are verified only by disposable PostgreSQL CI replay and have **not** been applied to managed staging.
- The managed Neon project is `learnwise` (`spring-cloud-84267029`); the staging branch is `think-tank-staging` (`br-still-cherry-baz7g5hk`).
- Read-only inspection of `learnwise_migration_history` on that branch returned exactly 001–013.
- The branch `think-tank-migration-rehearsal-20261106` (`br-plain-band-ba3mrbzi`) also contains only 001–013. It is not evidence that 014 onward has been rehearsed on that Neon branch.
- Disposable CI now replays all 19 numbered migrations on an isolated PostgreSQL 16 database, then runs schema integration and end-to-end tests.

## New migrations in this branch

- `014_ai_tutor_usage_and_budget.sql`
- `015_reviewed_lesson_content_and_progress.sql`
- `016_podcast_script_workflow.sql`
- `017_ai_tutor_platform_budget.sql`
- `018_student_saved_topics.sql`
- `019_student_data_rights_requests.sql`

Before staging migration, compare every unapplied file against the managed database's actual schema and migration checksums, inspect constraints/indexes/data dependencies, and rehearse an upgrade from a copy of the current 001–013 state. A clean-database replay alone does not prove an upgrade is safe.

## Required staged migration procedure

1. Take and verify a recoverable backup; agree RPO/RTO and rollback owner.
2. Create an isolated Neon branch from the current staging branch.
3. Compare migration source checksums with `learnwise_migration_history` and inspect actual table/index/constraint state.
4. Apply 014–019 only on the isolated branch, in order, with the reviewed migration runner.
5. Run schema integration, synthetic registration-to-results, saved lesson, assessment authoring/history, data-rights, payment-ledger and private-audio acceptance.
6. Compare pre/post row counts and audit continuity; verify rollback/recovery procedure.
7. Obtain explicit owner approval for managed staging migration and the matching code deployment.
8. Apply the reviewed migrations to managed staging in the approved window, verify exact migration history and application health, and stop on any unexpected schema drift.

No managed staging migration has been run as part of this work.

## Safety

- Do not rewrite or modify `main`.
- Do not force-push.
- Keep PR #1 draft and unmerged pending owner review.
- Do not deploy code against a database that is behind its required schema.
- If main advances, compare its changed files with the development branch before syncing.
