-- Student-facing assessment issue reporting and integrity appeals.
CREATE TABLE assessment_issue_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    question_id UUID,
    issue_type TEXT NOT NULL CHECK (issue_type IN (
      'integrity_appeal','question_error','technical_issue'
    )),
    details TEXT NOT NULL CHECK (char_length(details) BETWEEN 10 AND 2000),
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN (
      'submitted','under_review','resolved','dismissed'
    )),
    reviewer_admin_id UUID REFERENCES admin_users(id),
    reviewer_note TEXT CHECK (reviewer_note IS NULL OR char_length(reviewer_note) <= 2000),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT issue_report_question_pair_fk
      FOREIGN KEY (attempt_id, question_id)
      REFERENCES assessment_attempt_questions(attempt_id, question_id),
    CONSTRAINT question_error_requires_question
      CHECK (issue_type <> 'question_error' OR question_id IS NOT NULL)
);
CREATE INDEX assessment_issue_reports_queue_idx
  ON assessment_issue_reports(status, created_at);
CREATE INDEX assessment_issue_reports_student_idx
  ON assessment_issue_reports(student_id, created_at DESC);
CREATE INDEX assessment_issue_reports_attempt_idx
  ON assessment_issue_reports(attempt_id, created_at DESC);

CREATE OR REPLACE FUNCTION learnwise_validate_assessment_issue_owner()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE owner_id UUID;
BEGIN
  SELECT student_id INTO owner_id
  FROM assessment_attempts WHERE id = NEW.attempt_id;
  IF owner_id IS NULL OR owner_id <> NEW.student_id THEN
    RAISE EXCEPTION 'Assessment issue report owner does not match attempt owner';
  END IF;
  RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS assessment_issue_report_owner_guard ON assessment_issue_reports;
CREATE TRIGGER assessment_issue_report_owner_guard
  BEFORE INSERT ON assessment_issue_reports
  FOR EACH ROW EXECUTE FUNCTION learnwise_validate_assessment_issue_owner();
