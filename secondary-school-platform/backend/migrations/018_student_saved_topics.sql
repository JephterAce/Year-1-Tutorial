-- Private student bookmarks for published lesson topics.
CREATE TABLE IF NOT EXISTS student_saved_topics (
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (student_id, topic_id)
);

CREATE INDEX IF NOT EXISTS student_saved_topics_recent_idx
  ON student_saved_topics(student_id, created_at DESC);
