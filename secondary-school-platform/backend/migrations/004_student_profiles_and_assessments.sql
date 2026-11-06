-- Student profiles, consent records and versioned objective assessments.
-- Apply after backend/migrations/003_nerdc_curriculum_metadata.sql.
-- Keep answer_key server-side; never include it in student API projections.

ALTER TABLE students
  ADD COLUMN IF NOT EXISTS username TEXT,
  ADD COLUMN IF NOT EXISTS bio TEXT,
  ADD COLUMN IF NOT EXISTS profile_photo_key TEXT,
  ADD COLUMN IF NOT EXISTS profile_visibility TEXT NOT NULL DEFAULT 'private'
    CHECK (profile_visibility IN ('private')),
  ADD COLUMN IF NOT EXISTS privacy_notice_version TEXT,
  ADD COLUMN IF NOT EXISTS guardian_consent_status TEXT NOT NULL DEFAULT 'not_assessed'
    CHECK (guardian_consent_status IN ('not_assessed','not_required','pending','granted','denied')),
  ADD COLUMN IF NOT EXISTS marketing_opt_in BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS data_export_requested_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS deletion_requested_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS students_username_ci_unique
  ON students (lower(username)) WHERE username IS NOT NULL;

CREATE TABLE IF NOT EXISTS student_consent_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  consent_type TEXT NOT NULL CHECK (consent_type IN (
    'terms_of_service','privacy_notice','guardian_consent','optional_marketing'
  )),
  policy_version TEXT NOT NULL,
  granted BOOLEAN NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  withdrawn_at TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS student_consent_student_time_idx
  ON student_consent_records(student_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID NOT NULL REFERENCES subjects(id),
  class_level TEXT NOT NULL CHECK (class_level IN ('SS1','SS2','SS3')),
  title TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','archived')),
  version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
  allowed_question_counts INTEGER[] NOT NULL DEFAULT ARRAY[5,10,20,50,100],
  pass_mark_percent NUMERIC(5,2) NOT NULL DEFAULT 50
    CHECK (pass_mark_percent BETWEEN 0 AND 100),
  max_attempts INTEGER NOT NULL DEFAULT 1 CHECK (max_attempts > 0),
  available_from TIMESTAMPTZ,
  available_until TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(id, version),
  CHECK (available_until IS NULL OR available_from IS NULL OR available_until > available_from)
);

CREATE TABLE IF NOT EXISTS assessment_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  question_type TEXT NOT NULL CHECK (question_type IN (
    'single_choice','multiple_select','true_false','numeric','exact_text'
  )),
  prompt JSONB NOT NULL,
  options JSONB,
  answer_key JSONB NOT NULL,
  explanation TEXT,
  points NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (points > 0),
  numeric_tolerance NUMERIC(18,8),
  accepted_answers JSONB,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (question_type <> 'numeric' OR numeric_tolerance IS NULL OR numeric_tolerance >= 0)
);
CREATE INDEX IF NOT EXISTS assessment_questions_order_idx
  ON assessment_questions(assessment_id, sort_order) WHERE is_active = true;

CREATE TABLE IF NOT EXISTS assessment_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id),
  assessment_version INTEGER NOT NULL,
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  question_count INTEGER NOT NULL CHECK (question_count BETWEEN 1 AND 100),
  time_limit_seconds INTEGER NOT NULL CHECK (time_limit_seconds > 0),
  policy_version TEXT NOT NULL,
  agreement_recorded_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  deadline_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'briefing' CHECK (status IN (
    'briefing','in_progress','submitted','expired','terminated_integrity','under_review','graded'
  )),
  integrity_incidents INTEGER NOT NULL DEFAULT 0 CHECK (integrity_incidents BETWEEN 0 AND 3),
  integrity_review_required BOOLEAN NOT NULL DEFAULT false,
  score NUMERIC(10,2),
  maximum_score NUMERIC(10,2),
  percentage NUMERIC(5,2),
  passed BOOLEAN,
  submitted_at TIMESTAMPTZ,
  graded_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (assessment_id, assessment_version)
    REFERENCES assessments(id, version)
);
CREATE INDEX IF NOT EXISTS assessment_attempts_student_idx
  ON assessment_attempts(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS assessment_attempts_deadline_idx
  ON assessment_attempts(deadline_at) WHERE status = 'in_progress';

CREATE TABLE IF NOT EXISTS assessment_attempt_questions (
  attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES assessment_questions(id),
  display_order INTEGER NOT NULL,
  option_order JSONB,
  PRIMARY KEY(attempt_id, question_id),
  UNIQUE(attempt_id, display_order)
);

CREATE TABLE IF NOT EXISTS assessment_answers (
  attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES assessment_questions(id),
  answer JSONB,
  saved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_correct BOOLEAN,
  awarded_points NUMERIC(8,2),
  PRIMARY KEY(attempt_id, question_id)
);

CREATE TABLE IF NOT EXISTS assessment_integrity_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL CHECK (event_type IN (
    'visibility_hidden','fullscreen_exit','window_blur','incident_warning',
    'terminated','appeal_submitted'
  )),
  incident_number SMALLINT CHECK (incident_number BETWEEN 1 AND 3),
  server_received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS assessment_integrity_attempt_time_idx
  ON assessment_integrity_events(attempt_id, server_received_at);

CREATE TABLE IF NOT EXISTS student_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  notification_type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  related_entity_type TEXT,
  related_entity_id UUID,
  read_at TIMESTAMPTZ,
  delivery_status TEXT NOT NULL DEFAULT 'queued'
    CHECK (delivery_status IN ('queued','sent','failed','not_configured')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS student_notifications_inbox_idx
  ON student_notifications(student_id, created_at DESC);
