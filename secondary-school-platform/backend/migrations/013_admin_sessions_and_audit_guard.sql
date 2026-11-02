-- Dedicated admin session storage and append-only audit protection.
-- Apply after migrations 001-012 in a disposable PostgreSQL rehearsal first.
-- No admin login route is enabled by this migration.
CREATE TABLE IF NOT EXISTS admin_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_user_id UUID NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
  session_id_hash CHAR(64) NOT NULL UNIQUE,
  csrf_token_hash CHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  CHECK (expires_at > created_at),
  CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);
CREATE INDEX IF NOT EXISTS admin_sessions_user_active_idx
  ON admin_sessions(admin_user_id, expires_at)
  WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS admin_sessions_expiry_idx
  ON admin_sessions(expires_at);

-- Audit records are evidence, not mutable application state.
CREATE OR REPLACE FUNCTION learnwise_reject_audit_mutation()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'Audit events are append-only; corrections require a new event';
END;
$$;
DROP TRIGGER IF EXISTS audit_events_append_only ON audit_events;
CREATE TRIGGER audit_events_append_only
  BEFORE UPDATE OR DELETE ON audit_events
  FOR EACH ROW EXECUTE FUNCTION learnwise_reject_audit_mutation();

-- Ensure admin account identifiers remain normalised for login lookups.
CREATE UNIQUE INDEX IF NOT EXISTS admin_users_email_normalised_uidx
  ON admin_users(lower(trim(email)));
