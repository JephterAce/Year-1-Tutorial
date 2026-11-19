-- Enforce evidence requirements at the database boundary, not only in import code.
-- Apply after migration 009. Safe to re-run.
ALTER TABLE topics DROP CONSTRAINT IF EXISTS topics_term_mapping_status_check;
ALTER TABLE topics ADD CONSTRAINT topics_term_mapping_status_check
  CHECK (term_mapping_status IN ('official_term_allocation','school_scheme_verified','school_scheme_required','not_assigned','not_applicable'));
CREATE OR REPLACE FUNCTION learnwise_validate_curriculum_publication()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  source_row curriculum_source_records%ROWTYPE;
  version_row curriculum_versions%ROWTYPE;
BEGIN
  IF NEW.curriculum_status <> 'published' AND NEW.status <> 'published' THEN
    RETURN NEW;
  END IF;

  IF NEW.curriculum_status <> 'published' OR NEW.status <> 'published' THEN
    RAISE EXCEPTION 'Topic publication requires both topic status and curriculum status to be published';
  END IF;

  IF NEW.curriculum_version_id IS NULL OR NEW.curriculum_source_record_id IS NULL THEN
    RAISE EXCEPTION 'Published curriculum topics require a version and source record';
  END IF;

  SELECT * INTO version_row FROM curriculum_versions WHERE id = NEW.curriculum_version_id;
  IF NOT FOUND OR version_row.version_code <> 'nerdc_ssec_2025' OR version_row.status <> 'active' THEN
    RAISE EXCEPTION 'Only the active revised NERDC SSEC target version may be published';
  END IF;

  SELECT * INTO source_row FROM curriculum_source_records
    WHERE id = NEW.curriculum_source_record_id FOR KEY SHARE;
  IF NOT FOUND
     OR source_row.verification_status <> 'approved'
     OR source_row.curriculum_version_id <> NEW.curriculum_version_id
     OR source_row.class_level <> NEW.class_level
     OR source_row.subject_id <> NEW.subject_id THEN
    RAISE EXCEPTION 'Published topic source must be approved and match class, subject and curriculum version';
  END IF;

  IF COALESCE(trim(NEW.curriculum_evidence_note), '') = ''
     OR COALESCE(trim(NEW.curriculum_approved_by), '') = ''
     OR NEW.curriculum_approved_at IS NULL
     OR COALESCE(trim(source_row.source_section), '') = ''
     OR COALESCE(trim(source_row.reviewed_by), '') = ''
     OR source_row.reviewed_at IS NULL
     OR source_row.licence_status NOT IN ('metadata_only','permission_granted') THEN
    RAISE EXCEPTION 'Published topics require complete evidence, teacher review and rights metadata';
  END IF;

  IF NEW.term_mapping_status = 'official_term_allocation'
     AND (source_row.source_kind <> 'official_nerdc' OR NEW.term_id IS NULL) THEN
    RAISE EXCEPTION 'Official term allocation requires an official NERDC source and a term';
  END IF;

  IF NEW.term_mapping_status = 'school_scheme_verified'
     AND (source_row.source_kind <> 'school_scheme'
          OR COALESCE(trim(NEW.school_scheme_name), '') = ''
          OR NEW.term_id IS NULL) THEN
    RAISE EXCEPTION 'School term mapping requires a named school scheme and a term';
  END IF;

  IF NEW.term_mapping_status IN ('school_scheme_required','not_assigned') AND NEW.term_id IS NOT NULL THEN
    RAISE EXCEPTION 'Unverified term mappings must not carry a term assignment';
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS topics_curriculum_publication_guard ON topics;
CREATE TRIGGER topics_curriculum_publication_guard
  BEFORE INSERT OR UPDATE OF status, curriculum_status, curriculum_version_id,
    curriculum_source_record_id, curriculum_evidence_note, curriculum_approved_by,
    curriculum_approved_at, term_mapping_status, term_id, school_scheme_name
  ON topics FOR EACH ROW
  EXECUTE FUNCTION learnwise_validate_curriculum_publication();
