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

if __name__=="__main__": unittest.main()
