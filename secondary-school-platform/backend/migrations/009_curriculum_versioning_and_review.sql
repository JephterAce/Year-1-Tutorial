-- Curriculum versioning, cohort applicability and evidence-gated publication.
-- Apply after migrations 001-008 only in a reviewed non-production rehearsal first.
CREATE TABLE IF NOT EXISTS curriculum_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version_code TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  issuing_body TEXT NOT NULL DEFAULT 'Nigerian Educational Research and Development Council',
  official_source_url TEXT NOT NULL,
  effective_academic_year TEXT,
  is_target_version BOOLEAN NOT NULL DEFAULT false,
  status TEXT NOT NULL DEFAULT 'research'
    CHECK (status IN ('research','active','superseded','withdrawn')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO curriculum_versions
  (version_code,title,official_source_url,effective_academic_year,is_target_version,status,notes)
VALUES
  ('nerdc_ssec_2025','NERDC Revised Senior Secondary Education Curriculum (2025 framework)',
   'https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html',
   '2025/2026',true,'active',
   'Platform target version. Class-by-class subject/topic/term applicability still requires source capture and review.')
ON CONFLICT (version_code) DO UPDATE SET
  title=EXCLUDED.title, official_source_url=EXCLUDED.official_source_url,
  effective_academic_year=EXCLUDED.effective_academic_year,
  is_target_version=true, status='active', notes=EXCLUDED.notes, updated_at=now();

CREATE TABLE IF NOT EXISTS curriculum_cohort_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  class_level TEXT NOT NULL CHECK (class_level IN ('SS1','SS2','SS3')),
  cohort_label TEXT NOT NULL,
  academic_entry_year TEXT,
  curriculum_version_id UUID NOT NULL REFERENCES curriculum_versions(id),
  applicability_status TEXT NOT NULL DEFAULT 'pending_official_confirmation'
    CHECK (applicability_status IN ('pending_official_confirmation','confirmed','not_applicable')),
  confirmation_source_record_id UUID,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(class_level,cohort_label,curriculum_version_id)
);

ALTER TABLE curriculum_source_records
  ADD COLUMN IF NOT EXISTS curriculum_version_id UUID REFERENCES curriculum_versions(id),
  ADD COLUMN IF NOT EXISTS source_kind TEXT NOT NULL DEFAULT 'official_nerdc'
    CHECK (source_kind IN ('official_nerdc','school_scheme','teacher_reference','other')),
  ADD COLUMN IF NOT EXISTS source_checksum TEXT,
  ADD COLUMN IF NOT EXISTS licence_status TEXT NOT NULL DEFAULT 'metadata_only'
    CHECK (licence_status IN ('metadata_only','permission_requested','permission_granted','restricted','unknown')),
  ADD COLUMN IF NOT EXISTS reviewed_by TEXT,
  ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;

ALTER TABLE topics
  ALTER COLUMN term_id DROP NOT NULL,
  ADD COLUMN IF NOT EXISTS curriculum_version_id UUID REFERENCES curriculum_versions(id),
  ADD COLUMN IF NOT EXISTS curriculum_source_record_id UUID REFERENCES curriculum_source_records(id),
  ADD COLUMN IF NOT EXISTS curriculum_status TEXT NOT NULL DEFAULT 'unresearched'
    CHECK (curriculum_status IN ('unresearched','source_captured','mapped','term_pending','teacher_review','approved','published','rejected')),
  ADD COLUMN IF NOT EXISTS curriculum_evidence_note TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_approved_by TEXT,
  ADD COLUMN IF NOT EXISTS curriculum_approved_at TIMESTAMPTZ;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'curriculum_cohort_confirmation_source_fk'
      AND conrelid = 'curriculum_cohort_assignments'::regclass
  ) THEN
    ALTER TABLE curriculum_cohort_assignments
      ADD CONSTRAINT curriculum_cohort_confirmation_source_fk
      FOREIGN KEY (confirmation_source_record_id) REFERENCES curriculum_source_records(id);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS curriculum_versions_target_idx
  ON curriculum_versions(is_target_version,status);
CREATE INDEX IF NOT EXISTS curriculum_cohort_lookup_idx
  ON curriculum_cohort_assignments(class_level,applicability_status);
CREATE INDEX IF NOT EXISTS topics_curriculum_review_idx
  ON topics(curriculum_version_id,class_level,curriculum_status,status);

-- Published catalogue rows must be traceable to a version and a reviewed source.
-- Existing published rows are not silently blessed; this constraint is enforced
-- by the service policy for new publications and should be reconciled before launch.
