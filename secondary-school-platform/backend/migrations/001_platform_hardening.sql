-- Apply after DATABASE_SCHEMA.sql using a migration-capable database owner.
-- Never run migrations against the legacy Year 1 bot database.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE students
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN created_at SET DEFAULT now(),
  ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE subjects ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE terms ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE topics
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN created_at SET DEFAULT now(),
  ALTER COLUMN updated_at SET DEFAULT now();
ALTER TABLE lesson_assets
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE payment_transactions
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE entitlements
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN granted_at SET DEFAULT now();
ALTER TABLE quiz_questions ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE quiz_attempts
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN submitted_at SET DEFAULT now();
ALTER TABLE admin_users
  ALTER COLUMN id SET DEFAULT gen_random_uuid(),
  ALTER COLUMN created_at SET DEFAULT now();

-- Password hashes only; never store plaintext passwords.
ALTER TABLE students ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE students ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ;
ALTER TABLE students ADD COLUMN IF NOT EXISTS account_status TEXT NOT NULL DEFAULT 'pending'
  CHECK (account_status IN ('pending','active','suspended','closed'));

CREATE INDEX IF NOT EXISTS students_email_lookup_idx ON students (lower(email));
CREATE INDEX IF NOT EXISTS topics_published_catalogue_idx
  ON topics (class_level, subject_id, term_id, sort_order)
  WHERE status = 'published';

-- Webhook event ledger prevents duplicate fulfilment when Paystack retries events.
CREATE TABLE IF NOT EXISTS payment_webhook_events (
  id BIGSERIAL PRIMARY KEY,
  provider TEXT NOT NULL DEFAULT 'paystack',
  event_id TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  processed_at TIMESTAMPTZ,
  processing_error TEXT
);
