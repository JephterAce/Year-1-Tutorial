-- Draft podcast scripts generated only from approved lesson content.
-- Audio remains a separate private asset and must pass its own review.
CREATE TABLE IF NOT EXISTS podcast_scripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  lesson_content_id UUID NOT NULL,
  version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
  title TEXT NOT NULL,
  script_text TEXT NOT NULL CHECK (length(trim(script_text)) BETWEEN 100 AND 20000),
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','teacher_review','approved','rejected','archived')),
  generated_by_admin UUID REFERENCES admin_users(id),
  reviewed_by TEXT,
  reviewed_at TIMESTAMPTZ,
  audio_asset_id UUID REFERENCES lesson_assets(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(topic_id,version),
  FOREIGN KEY (lesson_content_id,topic_id)
    REFERENCES topic_lesson_content(id,topic_id),
  CHECK (
    (status='approved' AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL
      AND audio_asset_id IS NOT NULL)
    OR status<>'approved'
  )
);
CREATE INDEX IF NOT EXISTS podcast_scripts_topic_idx
  ON podcast_scripts(topic_id,version DESC);
