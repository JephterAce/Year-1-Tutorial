-- Revised NERDC curriculum metadata and source traceability.
-- Apply after migrations 001 and 002 using the migration owner.
ALTER TABLE subjects
  ADD COLUMN IF NOT EXISTS offering_group TEXT
    CHECK (offering_group IN ('core_compulsory','science','humanities','business','trade','other')),
  ADD COLUMN IF NOT EXISTS curriculum_name TEXT NOT NULL DEFAULT 'NERDC Revised Senior Secondary Education Curriculum',
  ADD COLUMN IF NOT EXISTS curriculum_version TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_source_url TEXT;

ALTER TABLE topics
  ADD COLUMN IF NOT EXISTS curriculum_theme TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_subtopic TEXT,
  ADD COLUMN IF NOT EXISTS learning_outcomes JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS term_mapping_status TEXT NOT NULL DEFAULT 'school_scheme_required'
    CHECK (term_mapping_status IN ('official_term_allocation','school_scheme_verified','school_scheme_required','not_applicable')),
  ADD COLUMN IF NOT EXISTS school_scheme_name TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_source_url TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_source_version TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_source_section TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_reviewed_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS curriculum_source_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID NOT NULL REFERENCES subjects(id),
  class_level TEXT NOT NULL CHECK (class_level IN ('SS1','SS2','SS3')),
  source_title TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_version TEXT,
  source_date DATE,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_section TEXT,
  notes TEXT,
  verification_status TEXT NOT NULL DEFAULT 'source_captured'
    CHECK (verification_status IN ('source_captured','mapped','teacher_review','approved','superseded')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS curriculum_sources_subject_class_idx
  ON curriculum_source_records(subject_id,class_level,verification_status);

CREATE INDEX IF NOT EXISTS topics_term_mapping_idx
  ON topics(class_level,subject_id,term_mapping_status,status);

-- No curriculum topics are inserted here: content must be captured and verified
-- from the class-specific official source before publication.
