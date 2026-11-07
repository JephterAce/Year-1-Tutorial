import unittest
from unittest.mock import patch
import rehearse_migrations as migrations
from audio_media import AudioAccessError, issue_audio_token, verify_audio_token, resolve_private_audio_path
from pathlib import Path
from tempfile import TemporaryDirectory

class MigrationSafetyTests(unittest.TestCase):
 def test_requires_explicit_rehearsal_url(self):
  with patch.dict("os.environ",{},clear=True):
   with self.assertRaises(RuntimeError): migrations.rehearsal_dsn()
 def test_refuses_remote_host(self):
  with patch.dict("os.environ",{"LEARNWISE_REHEARSAL_DATABASE_URL":"postgresql://x:y@db.example/learnwise_test"}):
   with self.assertRaises(RuntimeError): migrations.rehearsal_dsn()
 def test_refuses_default_database(self):
  with patch.dict("os.environ",{"LEARNWISE_REHEARSAL_DATABASE_URL":"postgresql://x:y@localhost/postgres"}):
   with self.assertRaises(RuntimeError): migrations.rehearsal_dsn()
 def test_migration_sequence_is_contiguous(self):
  nums=[int(p.name[:3]) for p in migrations.migration_files()]
  self.assertEqual(nums,list(range(1,len(nums)+1)))

class AudioTokenTests(unittest.TestCase):
 def setUp(self): self.p=patch.dict("os.environ",{"AUDIO_SIGNING_SECRET":"s"*48}); self.p.start()
 def tearDown(self): self.p.stop()
 def test_issue_and_verify(self):
  token=issue_audio_token("student","topic","lessons/topic/audio.mp3",True,now=1000)
  self.assertEqual(verify_audio_token(token,now=1100)["sub"],"student")
 def test_expiry_tamper_and_entitlement(self):
  token=issue_audio_token("s","t","audio.mp3",True,now=1000)
  with self.assertRaises(AudioAccessError): verify_audio_token(token,now=1400)
  with self.assertRaises(AudioAccessError): verify_audio_token(token+"x",now=1001)
  with self.assertRaises(AudioAccessError): issue_audio_token("s","t","audio.mp3",False)
 def test_path_traversal_rejected(self):
  with self.assertRaises(AudioAccessError): issue_audio_token("s","t","../secret.mp3",True)

 def test_private_storage_path_is_confined(self):
  with TemporaryDirectory() as root:
   p=Path(root)/"lesson.mp3";p.write_bytes(b"audio")
   self.assertEqual(resolve_private_audio_path(root,"lesson.mp3"),p.resolve())
   with self.assertRaises(AudioAccessError): resolve_private_audio_path(root,"../outside.mp3")


class NeonS3StorageConfigTests(unittest.TestCase):
 def test_s3_storage_requires_branch_scoped_environment(self):
  from audio_storage import storage_config, AudioStorageError
  with patch.dict("os.environ",{},clear=True):
   with self.assertRaises(AudioStorageError): storage_config()
 def test_s3_storage_reads_private_bucket_settings(self):
  from audio_storage import storage_config
  env={"AWS_ACCESS_KEY_ID":"id","AWS_SECRET_ACCESS_KEY":"secret",
       "AWS_ENDPOINT_URL_S3":"https://storage.example","AWS_REGION":"eu-central-1",
       "AUDIO_STORAGE_BUCKET":"learnwise-private-audio"}
  with patch.dict("os.environ",env,clear=True):
   cfg=storage_config()
  self.assertEqual(cfg["bucket"],"learnwise-private-audio")
  self.assertEqual(cfg["region"],"eu-central-1")


 def test_neon_storage_key_rejects_traversal(self):
  from audio_storage import validate_object_key, AudioStorageError
  self.assertEqual(validate_object_key("lesson/topic/audio.mp3"), "lesson/topic/audio.mp3")
  for key in ("../secret.mp3", "/absolute.mp3", "a\\\\b.mp3", "a//b.mp3"):
   with self.assertRaises(AudioStorageError): validate_object_key(key)

class StudentProgressUiTests(unittest.TestCase):
 def test_progress_page_is_connected_to_private_dashboard_records(self):
  page=Path(__file__).resolve().parents[1]/"frontend"/"index.html"
  source=page.read_text(encoding="utf-8")
  for marker in ("progressCompleted","progressPractice","progressAttempts",
                 "progressAverage","progressSubjects","progressRecent"):
   self.assertIn(marker,source)
  self.assertIn("function renderStudentProgress(data)",source)
  self.assertIn("studentApi('/api/v1/student/dashboard')",source)
  self.assertIn("encodeURIComponent(item.id)",source)
  self.assertNotIn("Progress tracking will become available",source)
 def test_podcast_library_uses_authorized_private_audio_access(self):
  page=Path(__file__).resolve().parents[1]/"frontend"/"index.html"
  source=page.read_text(encoding="utf-8")
  self.assertIn('data-page="podcasts"',source)
  self.assertIn("studentApi('/api/v1/student/podcasts')",source)
  self.assertIn("studentApi('/api/v1/topics/'+encodeURIComponent(item.topic_id)",source)
  self.assertIn("player.src=data.audio_url",source)
  self.assertIn("Podcast library",source)



class StudentAssessmentHistoryUiTests(unittest.TestCase):
 def test_history_displays_source_result_and_timestamp_fields(self):
  page=Path(__file__).resolve().parents[1]/"frontend"/"index.html"
  source=page.read_text(encoding="utf-8")
  self.assertIn("item.score+' / '+item.maximum_score",source)
  self.assertIn("item.submitted_at||item.started_at",source)
  self.assertIn("Human review requested",source)
  self.assertIn("Assessment attempts",source)


class StudentSavedLessonsUiTests(unittest.TestCase):
 def test_saved_lessons_page_uses_authenticated_api_and_safe_links(self):
  page=Path(__file__).resolve().parents[1]/"frontend"/"index.html"
  source=page.read_text(encoding="utf-8")
  self.assertIn('data-page="saved"',source)
  self.assertIn("studentApi('/api/v1/student/saved-lessons')",source)
  self.assertIn("studentApi('/api/v1/student/saved-lessons/'+encodeURIComponent(topic.id)",source)
  self.assertIn("studentApi('/api/v1/student/saved-lessons/'+encodeURIComponent(topicId)",source)
  self.assertIn("id=\"savedLessons\"",source)

if __name__ == "__main__":
 unittest.main()
