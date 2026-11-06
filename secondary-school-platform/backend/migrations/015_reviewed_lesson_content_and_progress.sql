-- Versioned, teacher-reviewed lesson notes and interactive practice.
-- Student topic progress is separate from media playback progress.
CREATE TABLE IF NOT EXISTS topic_lesson_content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
  content_json JSONB NOT NULL CHECK (jsonb_typeof(content_json) = 'object'),
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK (review_status IN ('draft','teacher_review','approved','rejected','archived')),
  created_by TEXT,
  approved_by TEXT,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(topic_id,version),
  UNIQUE(id,topic_id),
  CHECK (
    (review_status = 'approved' AND approved_by IS NOT NULL AND approved_at IS NOT NULL)
    OR review_status <> 'approved'
  )
);
CREATE INDEX IF NOT EXISTS topic_lesson_content_published_idx
  ON topic_lesson_content(topic_id,version DESC)
  WHERE review_status='approved';

CREATE TABLE IF NOT EXISTS lesson_practice_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL,
  lesson_content_id UUID NOT NULL,
  question_type TEXT NOT NULL CHECK (question_type IN ('single_choice','true_false','numeric')),
  prompt TEXT NOT NULL CHECK (length(trim(prompt)) BETWEEN 1 AND 2000),
  options JSONB,
  answer_key JSONB NOT NULL,
  explanation TEXT NOT NULL CHECK (length(trim(explanation)) BETWEEN 1 AND 4000),
  points NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (points > 0),
  sort_order INTEGER NOT NULL DEFAULT 0,
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK (review_status IN ('draft','teacher_review','approved','rejected')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (lesson_content_id,topic_id)
    REFERENCES topic_lesson_content(id,topic_id) ON DELETE CASCADE,
  CHECK (
    (question_type='single_choice' AND jsonb_typeof(options)='array')
    OR (question_type='true_false' AND options IS NULL)
    OR (question_type='numeric' AND options IS NULL)
  )
);
CREATE INDEX IF NOT EXISTS lesson_practice_questions_approved_idx
  ON lesson_practice_questions(topic_id,lesson_content_id,sort_order)
  WHERE review_status='approved';

CREATE TABLE IF NOT EXISTS student_topic_progress (
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  lesson_content_id UUID,
  last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(student_id,topic_id),
  FOREIGN KEY (lesson_content_id,topic_id)
    REFERENCES topic_lesson_content(id,topic_id)
);
CREATE INDEX IF NOT EXISTS student_topic_progress_recent_idx
  ON student_topic_progress(student_id,updated_at DESC);

ALTER TABLE lesson_practice_questions
  ADD CONSTRAINT lesson_practice_question_topic_unique UNIQUE(id,topic_id);

CREATE TABLE IF NOT EXISTS student_lesson_practice_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  question_id UUID NOT NULL,
  submitted_answer JSONB NOT NULL,
  is_correct BOOLEAN NOT NULL,
  attempted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (question_id,topic_id)
    REFERENCES lesson_practice_questions(id,topic_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS student_lesson_practice_attempts_recent_idx
  ON student_lesson_practice_attempts(student_id,attempted_at DESC);
