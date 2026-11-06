-- Platform-wide AI tutor spend caps in addition to per-student quotas.
CREATE TABLE IF NOT EXISTS ai_tutor_platform_usage (
  usage_date DATE PRIMARY KEY,
  request_count BIGINT NOT NULL DEFAULT 0 CHECK (request_count >= 0),
  estimated_cost_microusd BIGINT NOT NULL DEFAULT 0 CHECK (estimated_cost_microusd >= 0),
  estimated_input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (estimated_input_tokens >= 0),
  reserved_output_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reserved_output_tokens >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
