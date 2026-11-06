# Migration and main-branch reconciliation

Checked 2026-11-03.

## Main-branch changes preserved

The current `main` head is `5d6d93ceec31ff3eb6851d567e4d61f7477bc492`, two commits ahead of the PR's previous base `ac472be3e6de796ce5f6c3ea4e5f343dc172cd1d`.

The two intervening main commits add:
- `AUTOMATED_ASSESSMENT_AND_STUDENT_PROFILES.md` — product and acceptance-test specification.
- `migrations/004_student_profiles_and_assessments.sql` — an earlier schema migration.

Both files are retained verbatim on this development branch so the PR does not delete main's work.

## Canonical migration sequence for this branch

For the Learnwise backend implementation, the canonical sequence is `backend/migrations/001` through `backend/migrations/013`, following `DATABASE_SCHEMA.sql`. These migrations were rehearsed on the dedicated Neon staging branch `learnwise-staging-rehearsal` and recorded in `learnwise_migration_history`.

The root-level `migrations/004_student_profiles_and_assessments.sql` is preserved for history/compatibility only. **Do not apply it on top of the canonical backend migration sequence.** It overlaps with the newer backend migration 004 and uses a different profile/consent schema. Reconcile any future changes into the canonical backend sequence through a new numbered migration, with a clean-database rehearsal and upgrade test.

## Safety

- Do not rewrite or modify `main`.
- Do not force-push.
- Keep PR #1 draft and unmerged pending owner review.
- If main advances again, compare its changed files with the development branch before syncing.
