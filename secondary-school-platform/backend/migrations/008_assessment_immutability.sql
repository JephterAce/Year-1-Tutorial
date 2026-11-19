-- Freeze assessment content after publication and snapshot it per attempt.
-- Apply after migrations 001-007. A revised assessment is a new assessment record/version.
ALTER TABLE assessment_attempt_questions
  ADD COLUMN IF NOT EXISTS question_snapshot JSONB,
  ADD COLUMN IF NOT EXISTS answer_key_snapshot JSONB,
  ADD COLUMN IF NOT EXISTS points_snapshot NUMERIC(8,2),
  ADD COLUMN IF NOT EXISTS numeric_tolerance_snapshot NUMERIC(18,8),
  ADD COLUMN IF NOT EXISTS accepted_answers_snapshot JSONB;

CREATE OR REPLACE FUNCTION learnwise_reject_published_assessment_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status = 'published' THEN
      RAISE EXCEPTION 'Published assessments are immutable; create a new version';
    END IF;
    RETURN OLD;
  END IF;
  IF OLD.status = 'published' THEN
    RAISE EXCEPTION 'Published assessments are immutable; create a new version';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS assessments_immutable_after_publish ON assessments;
CREATE TRIGGER assessments_immutable_after_publish
  BEFORE UPDATE OR DELETE ON assessments
  FOR EACH ROW EXECUTE FUNCTION learnwise_reject_published_assessment_change();

CREATE OR REPLACE FUNCTION learnwise_reject_published_question_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE parent_status TEXT;
BEGIN
  SELECT status INTO parent_status FROM assessments
    WHERE id = CASE WHEN TG_OP = 'DELETE' THEN OLD.assessment_id ELSE NEW.assessment_id END;
  IF parent_status = 'published' THEN
    RAISE EXCEPTION 'Questions in published assessments are immutable; create a new version';
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS assessment_questions_immutable_after_publish ON assessment_questions;
CREATE TRIGGER assessment_questions_immutable_after_publish
  BEFORE UPDATE OR DELETE ON assessment_questions
  FOR EACH ROW EXECUTE FUNCTION learnwise_reject_published_question_change();

-- Snapshots must be populated by the trusted attempt-start transaction before
-- students can fetch the question. Student APIs must never project answer_key_snapshot.
