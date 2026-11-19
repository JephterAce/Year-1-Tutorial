-- Database-enforced accounting for AI tutor requests and conservative cost reservations.
-- Apply after migrations 001-013. No student usage is created by this migration.
CREATE TABLE IF NOT EXISTS student_ai_tutor_usage (
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  usage_date DATE NOT NULL DEFAULT (now() AT TIME ZONE 'UTC')::date,
  request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0),
  estimated_cost_microusd BIGINT NOT NULL DEFAULT 0 CHECK (estimated_cost_microusd >= 0),
  estimated_input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (estimated_input_tokens >= 0),
  reserved_output_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reserved_output_tokens >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(student_id, usage_date)
);
CREATE INDEX IF NOT EXISTS student_ai_tutor_usage_month_idx
  ON student_ai_tutor_usage(student_id, usage_date);
