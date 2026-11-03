-- Student profile foundations and automatically scored assessments.
-- Apply only to the dedicated secondary-school database after backup/review.

ALTER TABLE students
  ADD COLUMN IF NOT EXISTS username TEXT,
  ADD COLUMN IF NOT EXISTS bio TEXT,
  ADD COLUMN IF NOT EXISTS profile_image_key TEXT,
  ADD COLUMN IF NOT EXISTS profile_visibility TEXT NOT NULL DEFAULT 'private'
    CHECK (profile_visibility IN ('private','classmates','public')),
  ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS guardian_consent_status TEXT NOT NULL DEFAULT 'not_required'
    CHECK (guardian_consent_status IN ('not_required','pending','granted','withdrawn')),
  ADD COLUMN IF NOT EXISTS privacy_notice_version TEXT,
  ADD COLUMN IF NOT EXISTS marketing_opt_in BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS marketing_opt_in_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS data_export_requested_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS deletion_requested_at TIMESTAMPTZ;

ALTER TABLE students
  ADD CONSTRAINT students_username_format
    CHECK (username IS NULL OR username ~ '^[a-zA-Z0-9_]{3,24}$'),
  ADD CONSTRAINT students_bio_length
    CHECK (bio IS NULL OR char_length(bio) <= 240);

CREATE UNIQUE INDEX IF NOT EXISTS students_username_unique
  ON students (lower(username)) WHERE username IS NOT NULL;

CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY,
  topic_id UUID NOT NULL REFERENCES topics(id),
  title TEXT NOT NULL,
  instructions TEXT,
  assessment_type TEXT NOT NULL DEFAULT 'practice'
    CHECK (assessment_type IN ('practice','graded','diagnostic')),
  duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds BETWEEN 60 AND 14400),
  max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 20),
  pass_mark_percent NUMERIC(5,2) NOT NULL DEFAULT 50
    CHECK (pass_mark_percent BETWEEN 0 AND 100),
  shuffle_questions BOOLEAN NOT NULL DEFAULT true,
  shuffle_options BOOLEAN NOT NULL DEFAULT true,
  show_explanations_after_submit BOOLEAN NOT NULL DEFAULT true,
  result_release TEXT NOT NULL DEFAULT 'immediate'
    CHECK (result_release IN ('immediate','scheduled','manual')),
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','review','published','archived')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assessment_questions (
  id UUID PRIMARY KEY,
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  question_type TEXT NOT NULL
    CHECK (question_type IN ('single_choice','multiple_select','true_false','numeric','exact_text')),
  prompt JSONB NOT NULL,
  options JSONB NOT NULL DEFAULT '[]'::jsonb,
  answer_key JSONB NOT NULL,
  explanation TEXT,
  points NUMERIC(7,2) NOT NULL DEFAULT 1 CHECK (points > 0),
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON COLUMN assessment_questions.answer_key IS
  'Private grading key. Never include in student-facing API responses.';

CREATE TABLE IF NOT EXISTS assessment_attempts (
  id UUID PRIMARY KEY,
  assessment_id UUID NOT NULL REFERENCES assessments(id),
  student_id UUID NOT NULL REFERENCES students(id),
  attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
  status TEXT NOT NULL DEFAULT 'in_progress'
    CHECK (status IN ('in_progress','submitted','graded','expired','voided')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  submitted_at TIMESTAMPTZ,
  auto_graded_at TIMESTAMPTZ,
  score_points NUMERIC(9,2),
  total_points NUMERIC(9,2),
  score_percent NUMERIC(5,2),
  passed BOOLEAN,
  result_released_at TIMESTAMPTZ,
  UNIQUE (assessment_id, student_id, attempt_number)
);

CREATE TABLE IF NOT EXISTS assessment_answers (
  id UUID PRIMARY KEY,
  attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES assessment_questions(id),
  response JSONB NOT NULL DEFAULT 'null'::jsonb,
  awarded_points NUMERIC(7,2),
  is_correct BOOLEAN,
  graded_at TIMESTAMPTZ,
  UNIQUE (attempt_id, question_id)
);

CREATE TABLE IF NOT EXISTS student_notifications (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL REFERENCES students(id),
  notification_type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  related_entity_type TEXT,
  related_entity_id UUID,
  delivery_channel TEXT NOT NULL DEFAULT 'in_app'
    CHECK (delivery_channel IN ('in_app','email')),
  delivery_status TEXT NOT NULL DEFAULT 'queued'
    CHECK (delivery_status IN ('queued','sent','failed','read')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS consent_records (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL REFERENCES students(id),
  consent_type TEXT NOT NULL
    CHECK (consent_type IN ('terms','privacy_notice','guardian_consent','marketing','external_reuse')),
  notice_version TEXT NOT NULL,
  granted BOOLEAN NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  withdrawn_at TIMESTAMPTZ,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS assessments_topic_status_idx ON assessments(topic_id,status);
CREATE INDEX IF NOT EXISTS assessment_questions_assessment_idx ON assessment_questions(assessment_id,sort_order);
CREATE INDEX IF NOT EXISTS assessment_attempts_student_idx ON assessment_attempts(student_id,submitted_at DESC);
CREATE INDEX IF NOT EXISTS notifications_student_idx ON student_notifications(student_id,created_at DESC);
CREATE INDEX IF NOT EXISTS consent_student_type_idx ON consent_records(student_id,consent_type,recorded_at DESC);
