-- Student-initiated data-rights requests with an auditable administrator review trail.
-- This migration records requests only; it does not automatically erase student records.
CREATE TABLE IF NOT EXISTS student_data_rights_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  request_type TEXT NOT NULL CHECK (request_type IN ('access_export','correction','deletion','restriction')),
  status TEXT NOT NULL DEFAULT 'submitted'
    CHECK (status IN ('submitted','under_review','awaiting_information','resolved','declined','withdrawn')),
  request_note TEXT,
  resolution_note TEXT,
  reviewed_by_admin_id UUID REFERENCES admin_users(id),
  reviewed_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (request_note IS NULL OR length(request_note) <= 2000),
  CHECK (resolution_note IS NULL OR length(resolution_note) <= 2000),
  CHECK (status NOT IN ('resolved','declined') OR
         (reviewed_by_admin_id IS NOT NULL AND reviewed_at IS NOT NULL AND resolution_note IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS student_data_rights_student_recent_idx
  ON student_data_rights_requests(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS student_data_rights_queue_idx
  ON student_data_rights_requests(status, created_at)
  WHERE status IN ('submitted','under_review','awaiting_information');

CREATE UNIQUE INDEX IF NOT EXISTS student_data_rights_one_open_request_idx
  ON student_data_rights_requests(student_id, request_type)
  WHERE status IN ('submitted','under_review','awaiting_information');

CREATE INDEX IF NOT EXISTS student_data_rights_admin_review_idx
  ON student_data_rights_requests(reviewed_by_admin_id, reviewed_at DESC)
  WHERE reviewed_by_admin_id IS NOT NULL;
