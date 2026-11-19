-- Preserve the evidence behind published Learnwise curriculum topics.
-- Apply after 010. Create a replacement source and re-review topics rather than
-- editing or withdrawing a source already used by published content.
CREATE OR REPLACE FUNCTION learnwise_protect_published_curriculum_source()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  source_id UUID;
BEGIN
  source_id := OLD.id;
  IF EXISTS (
    SELECT 1 FROM topics
    WHERE curriculum_source_record_id = source_id
      AND status = 'published'
      AND curriculum_status = 'published'
  ) THEN
    RAISE EXCEPTION
      'A curriculum source referenced by published topics is immutable; create and review a replacement source first';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS curriculum_source_published_immutability ON curriculum_source_records;
CREATE TRIGGER curriculum_source_published_immutability
  BEFORE UPDATE OR DELETE ON curriculum_source_records
  FOR EACH ROW
  EXECUTE FUNCTION learnwise_protect_published_curriculum_source();

CREATE OR REPLACE FUNCTION learnwise_protect_published_curriculum_version()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM topics
    WHERE curriculum_version_id = OLD.id
      AND status = 'published'
      AND curriculum_status = 'published'
  ) AND (
    NEW.version_code IS DISTINCT FROM OLD.version_code
    OR NEW.status IS DISTINCT FROM OLD.status
    OR NEW.official_source_url IS DISTINCT FROM OLD.official_source_url
    OR NEW.is_target_version IS DISTINCT FROM OLD.is_target_version
  ) THEN
    RAISE EXCEPTION
      'A curriculum version used by published topics cannot be changed; create a new version and migrate topics through review';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS curriculum_version_published_immutability ON curriculum_versions;
CREATE TRIGGER curriculum_version_published_immutability
  BEFORE UPDATE ON curriculum_versions
  FOR EACH ROW
  EXECUTE FUNCTION learnwise_protect_published_curriculum_version();
