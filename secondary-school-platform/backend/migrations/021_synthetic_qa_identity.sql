-- Explicitly isolate short-lived staging QA identities from real learners.
-- No consent records are created by the QA provisioning path.
ALTER TABLE students
  ADD COLUMN IF NOT EXISTS is_synthetic_qa BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS synthetic_qa_expires_at TIMESTAMPTZ;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'students_synthetic_qa_expiry_pair'
      AND conrelid = 'students'::regclass
  ) THEN
    ALTER TABLE students
      ADD CONSTRAINT students_synthetic_qa_expiry_pair
      CHECK (
        (is_synthetic_qa = true AND synthetic_qa_expires_at IS NOT NULL)
        OR
        (is_synthetic_qa = false AND synthetic_qa_expires_at IS NULL)
      );
  END IF;
END $$;

-- At most one pending or active synthetic identity may exist at a time.
CREATE UNIQUE INDEX IF NOT EXISTS students_single_active_synthetic_qa_uidx
  ON students(is_synthetic_qa)
  WHERE is_synthetic_qa = true AND account_status IN ('pending','active');

-- A QA invitation has its own token purpose and cannot be confused with public
-- registration verification or password-reset tokens.
ALTER TABLE identity_tokens
  DROP CONSTRAINT IF EXISTS identity_tokens_purpose_check;
ALTER TABLE identity_tokens
  ADD CONSTRAINT identity_tokens_purpose_check
  CHECK (purpose IN (
    'verify_email',
    'verify_qa_email',
    'reset_student_password',
    'reset_admin_password'
  ));

ALTER TABLE identity_tokens
  DROP CONSTRAINT IF EXISTS identity_tokens_check;
ALTER TABLE identity_tokens
  ADD CONSTRAINT identity_tokens_identity_pair_check
  CHECK (
    (student_id IS NOT NULL AND admin_user_id IS NULL
      AND purpose IN ('verify_email','verify_qa_email','reset_student_password'))
    OR
    (student_id IS NULL AND admin_user_id IS NOT NULL
      AND purpose = 'reset_admin_password')
  );

CREATE INDEX IF NOT EXISTS students_synthetic_qa_expiry_idx
  ON students(synthetic_qa_expires_at)
  WHERE is_synthetic_qa = true;
