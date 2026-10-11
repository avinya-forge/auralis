import unittest
from unittest.mock import MagicMock, patch
import sys
import importlib


class TestSpectrogramService(unittest.TestCase):
    def setUp(self):
        # Mock librosa and numpy
        self.mock_librosa = MagicMock()
        self.mock_numpy = MagicMock()

        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "librosa": self.mock_librosa,
                "numpy": self.mock_numpy,
            },
        )
        self.modules_patcher.start()

        import src.services.spectrogram_service

        self.module = importlib.reload(src.services.spectrogram_service)
        self.SpectrogramService = self.module.SpectrogramService

        self.service = self.SpectrogramService()

    def tearDown(self):
        self.modules_patcher.stop()
        if "src.services.spectrogram_service" in sys.modules:
            import src.services.spectrogram_service

            importlib.reload(src.services.spectrogram_service)

    def test_init_missing_dependencies(self):
        with patch.dict(sys.modules):
            sys.modules["librosa"] = None
            with patch("src.services.spectrogram_service.logger") as mock_logger:
                service = self.SpectrogramService()
                self.assertFalse(service.has_dependencies)
                mock_logger.warning.assert_called_with(
                    "Librosa or numpy not installed. Spectrogram features disabled."
                )

    def test_generate_mel_spectrogram_success(self):
        self.mock_librosa.load.return_value = (MagicMock(), 22050)
        self.mock_librosa.feature.melspectrogram.return_value = MagicMock()
        self.mock_librosa.power_to_db.return_value = "spectrogram_db"

        result = self.service.generate_mel_spectrogram("test.mp3")

        self.assertEqual(result, "spectrogram_db")
        self.mock_librosa.load.assert_called_with("test.mp3", duration=30)
        self.mock_librosa.feature.melspectrogram.assert_called()
        self.mock_librosa.power_to_db.assert_called()

    def test_generate_mel_spectrogram_no_deps(self):
        self.service.has_dependencies = False
        result = self.service.generate_mel_spectrogram("test.mp3")
        self.assertIsNone(result)

    def test_generate_mel_spectrogram_error(self):
        self.mock_librosa.load.side_effect = Exception("Load error")
        with patch("src.services.spectrogram_service.logger") as mock_logger:
            result = self.service.generate_mel_spectrogram("test.mp3")
            self.assertIsNone(result)
            mock_logger.error.assert_called()

    def test_process_batch_success(self):
        with patch.object(self.service, "generate_song_id") as mock_gen_id:
            mock_gen_id.side_effect = lambda path: f"id_{path}"

            paths = ["path1.mp3", "path2.mp3", "path3.mp3"]
            result = self.service.process_batch(paths, max_workers=2)

            self.assertEqual(len(result), 3)
            self.assertEqual(result["path1.mp3"], "id_path1.mp3")
            self.assertEqual(result["path2.mp3"], "id_path2.mp3")
            self.assertEqual(result["path3.mp3"], "id_path3.mp3")

    def test_process_batch_no_deps(self):
        self.service.has_dependencies = False
        paths = ["path1.mp3", "path2.mp3"]
        result = self.service.process_batch(paths)

        self.assertEqual(len(result), 2)
        self.assertIsNone(result["path1.mp3"])
        self.assertIsNone(result["path2.mp3"])

    def test_process_batch_error(self):
        with patch.object(self.service, "generate_song_id") as mock_gen_id:

            def side_effect(path):
                if path == "error.mp3":
                    raise Exception("Test error")
                return f"id_{path}"

            mock_gen_id.side_effect = side_effect

            paths = ["good.mp3", "error.mp3"]
            with patch("src.services.spectrogram_service.logger") as mock_logger_batch:
                result = self.service.process_batch(paths)

                self.assertEqual(result["good.mp3"], "id_good.mp3")
                self.assertIsNone(result["error.mp3"])
                mock_logger_batch.error.assert_called()

    def test_find_duplicates_in_batch(self):
        with patch.object(self.service, "process_batch") as mock_process:
            mock_process.return_value = {
                "file1.mp3": "id1",
                "file2.mp3": "id2",
                "file3.mp3": "id1",
                "file4.mp3": None,
                "file5.mp3": "id3",
            }

            paths = ["file1.mp3", "file2.mp3", "file3.mp3", "file4.mp3", "file5.mp3"]
            duplicates = self.service.find_duplicates_in_batch(paths)

            self.assertIn("id1", duplicates)
            self.assertEqual(len(duplicates["id1"]), 2)
            self.assertIn("file1.mp3", duplicates["id1"])
            self.assertIn("file3.mp3", duplicates["id1"])

            # id2, id3, and None should not be in duplicates
            self.assertNotIn("id2", duplicates)
            self.assertNotIn("id3", duplicates)
            self.assertNotIn(None, duplicates)

    @patch("src.services.spectrogram_service.hashlib")
    def test_generate_song_id_success(self, mock_hashlib):
        # We need numpy to be a real mock returning bytes
        with patch.object(self.service, "generate_mel_spectrogram") as mock_gen_mel:
            mock_gen_mel.return_value = "spectrogram_db"

            self.mock_numpy.mean.return_value = "mean"
            self.mock_numpy.var.return_value = "var"
            self.mock_numpy.concatenate.return_value = "concat"

            mock_rounded = MagicMock()
            mock_rounded.tobytes.return_value = b"testbytes"
            self.mock_numpy.round.return_value = mock_rounded

            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "testhash123"
            mock_hashlib.sha256.return_value = mock_hash

            result = self.service.generate_song_id("test.mp3")

            self.assertEqual(result, "testhash123")
            mock_gen_mel.assert_called_with("test.mp3")
            mock_hashlib.sha256.assert_called_with(b"testbytes")

    def test_generate_song_id_no_spectrogram(self):
        with patch.object(self.service, "generate_mel_spectrogram") as mock_gen_mel:
            mock_gen_mel.return_value = None
            result = self.service.generate_song_id("test.mp3")
            self.assertIsNone(result)
