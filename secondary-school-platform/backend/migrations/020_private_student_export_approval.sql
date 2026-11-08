-- Add a separate approval gate and manifest pointer for private asynchronous exports.
-- Existing self-service student JSON exports are unchanged. No export is processed until
-- a different active administrator approves it and a private export bucket is configured.
ALTER TABLE student_data_exports
  ADD COLUMN IF NOT EXISTS approved_by_admin_id UUID REFERENCES admin_users(id),
  ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS manifest_storage_key TEXT,
  ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS attempt_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'student_data_exports_distinct_approver'
      AND conrelid = 'student_data_exports'::regclass
  ) THEN
    ALTER TABLE student_data_exports
      ADD CONSTRAINT student_data_exports_distinct_approver
      CHECK (approved_by_admin_id IS NULL OR approved_by_admin_id <> requested_by_admin_id);
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'student_data_exports_approval_pair'
      AND conrelid = 'student_data_exports'::regclass
  ) THEN
    ALTER TABLE student_data_exports
      ADD CONSTRAINT student_data_exports_approval_pair
      CHECK (approved_at IS NULL OR approved_by_admin_id IS NOT NULL);
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'student_data_exports_attempt_count'
      AND conrelid = 'student_data_exports'::regclass
  ) THEN
    ALTER TABLE student_data_exports
      ADD CONSTRAINT student_data_exports_attempt_count
      CHECK (attempt_count BETWEEN 0 AND 3);
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'student_data_exports_completed_manifest'
      AND conrelid = 'student_data_exports'::regclass
  ) THEN
    ALTER TABLE student_data_exports
      ADD CONSTRAINT student_data_exports_completed_manifest
      CHECK (status <> 'completed' OR manifest_storage_key IS NOT NULL);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS student_data_exports_approved_queue_idx
  ON student_data_exports(status, approved_at, requested_at)
  WHERE status IN ('queued','processing') AND approved_at IS NOT NULL;
