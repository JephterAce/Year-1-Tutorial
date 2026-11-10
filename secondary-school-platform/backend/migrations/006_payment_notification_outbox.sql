-- Durable, idempotent fulfilment and email outbox for verified payments.
-- Apply after migrations 001-005. Never apply to the legacy bot database.

CREATE TABLE IF NOT EXISTS payment_notification_outbox (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id UUID NOT NULL REFERENCES payment_transactions(id),
  event_type TEXT NOT NULL CHECK (event_type IN ('owner_payment_alert')),
  dedupe_key TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued'
    CHECK (status IN ('queued','processing','sent','retry','dead_letter')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  locked_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  last_error_code TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS payment_notification_outbox_ready_idx
  ON payment_notification_outbox(available_at, created_at)
  WHERE status IN ('queued','retry');

CREATE INDEX IF NOT EXISTS payment_webhook_events_reference_idx
  ON payment_webhook_events ((payload->>'reference'), received_at DESC);
