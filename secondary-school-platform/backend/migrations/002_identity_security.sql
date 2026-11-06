-- Identity/security support tables. Apply after 001_platform_hardening.sql.
-- Tokens are stored as SHA-256 hashes only; raw tokens are delivered out-of-band.
ALTER TABLE admin_users
  ADD COLUMN IF NOT EXISTS password_hash TEXT,
  ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;

ALTER TABLE students
  ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS identity_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  admin_user_id UUID REFERENCES admin_users(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL CHECK (purpose IN ('verify_email','reset_student_password','reset_admin_password')),
  token_hash CHAR(64) NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  consumed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (
    (student_id IS NOT NULL AND admin_user_id IS NULL
      AND purpose IN ('verify_email','reset_student_password'))
    OR
    (student_id IS NULL AND admin_user_id IS NOT NULL
      AND purpose = 'reset_admin_password')
  )
);

CREATE INDEX IF NOT EXISTS identity_tokens_student_purpose_idx
  ON identity_tokens(student_id, purpose, expires_at)
  WHERE consumed_at IS NULL;

CREATE INDEX IF NOT EXISTS identity_tokens_admin_purpose_idx
  ON identity_tokens(admin_user_id, purpose, expires_at)
  WHERE consumed_at IS NULL;

-- Supports explicit session revocation if/when server-side sessions are enabled.
CREATE TABLE IF NOT EXISTS revoked_sessions (
  session_id_hash CHAR(64) PRIMARY KEY,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS revoked_sessions_expiry_idx ON revoked_sessions(expires_at);
