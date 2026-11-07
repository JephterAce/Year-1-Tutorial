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


## Read-only source checksum comparison — 7 November 2026

Queried the managed staging table `learnwise_migration_history` and compared each recorded `source_blob_sha` with the GitHub blob SHA for the same canonical backend migration file on the development branch.

<badge>13/13 applied migrations match</badge>

| Migration | Managed recorded SHA | Development GitHub blob SHA | Result |
|---|---|---|---|
| 001_platform_hardening | 7447de19cd4df12ac8c09ab1b6c36888a653a1d7 | 7447de19cd4df12ac8c09ab1b6c36888a653a1d7 | Match |
| 002_identity_security | 2b0a6128c8b4922585f796f26809a55c87bdc811 | 2b0a6128c8b4922585f796f26809a55c87bdc811 | Match |
| 003_nerdc_curriculum_metadata | bfa5d05a0529417142e6541e3cc95f44b058e44a | bfa5d05a0529417142e6541e3cc95f44b058e44a | Match |
| 004_student_profiles_and_assessments | 137f3ea137dff054c2530ad51d67cb1711f7ef59 | 137f3ea137dff054c2530ad51d67cb1711f7ef59 | Match |
| 005_student_data_exports | 20e77fe54697c8f9e942e0e41e98507f376030b8 | 20e77fe54697c8f9e942e0e41e98507f376030b8 | Match |
| 006_payment_notification_outbox | 57a1c9e6a710df9d1e6c72d17cdde27f37f07267 | 57a1c9e6a710df9d1e6c72d17cdde27f37f07267 | Match |
| 007_student_sessions_and_rate_limits | 3cf339eb3ffd5b1243e69622bff29bf2638c8a59 | 3cf339eb3ffd5b1243e69622bff29bf2638c8a59 | Match |
| 008_assessment_immutability | 492d3c250c68fa552183bfad9abfe596c64318ec | 492d3c250c68fa552183bfad9abfe596c64318ec | Match |
| 009_curriculum_versioning_and_review | b2a5e24c851921e0e01206742d98b3eb7469d3f7 | b2a5e24c851921e0e01206742d98b3eb7469d3f7 | Match |
| 010_curriculum_publication_guard | 5a676852ee969098c503cd841dfcf177d8da3e92 | 5a676852ee969098c503cd841dfcf177d8da3e92 | Match |
| 011_curriculum_source_immutability | 15ff126155bfcc8c157183e9b4a6911076fc6307 | 15ff126155bfcc8c157183e9b4a6911076fc6307 | Match |
| 012_assessment_issue_reporting | 1bb1c8dffe53e7feb73fbba14ef7b84c48226d6a | 1bb1c8dffe53e7feb73fbba14ef7b84c48226d6a | Match |
| 013_admin_sessions_and_audit_guard | 548e463479b322b4197e8a605f63d03b6993fdf8 | 548e463479b322b4197e8a605f63d03b6993fdf8 | Match |

This establishes that the 13 applied migration source blobs match the repository files. It does not establish that the pending migrations 014–019 are safe to apply to live staging; they remain unapplied and require upgrade rehearsal from the current 001–013 state plus explicit approval.
