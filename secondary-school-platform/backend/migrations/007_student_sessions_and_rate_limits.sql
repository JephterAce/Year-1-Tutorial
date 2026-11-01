-- Server-side student sessions and registration throttling.
-- Apply after migrations 001-006 on the dedicated Learnwise database only.
CREATE TABLE IF NOT EXISTS student_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  session_id_hash CHAR(64) NOT NULL UNIQUE,
  csrf_token_hash CHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS student_sessions_active_idx
  ON student_sessions(student_id, expires_at) WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS auth_rate_limits (
  action_key TEXT NOT NULL,
  subject_hash CHAR(64) NOT NULL,
  window_started_at TIMESTAMPTZ NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  blocked_until TIMESTAMPTZ,
  PRIMARY KEY(action_key, subject_hash)
);
CREATE INDEX IF NOT EXISTS auth_rate_limits_blocked_idx
  ON auth_rate_limits(blocked_until) WHERE blocked_until IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS students_email_ci_unique
  ON students(lower(email)) WHERE email IS NOT NULL;
