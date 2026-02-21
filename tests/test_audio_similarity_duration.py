import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestAudioSimilarityDuration(unittest.TestCase):

    def test_find_duplicates_duration_extraction(self):
        """Test that duration is extracted using mutagen if missing from metadata"""

        # Setup mocks
        mock_numpy = MagicMock()
        mock_mutagen = MagicMock()
        mock_librosa = MagicMock()
        mock_soundfile = MagicMock()
        mock_sklearn = MagicMock()
        mock_pydub = MagicMock()

        # Config mock mutagen.File
        mock_audio = MagicMock()
        mock_audio.info.length = 120.5
        mock_mutagen.File.return_value = mock_audio

        mocks = {
            "numpy": mock_numpy,
            "mutagen": mock_mutagen,
            "librosa": mock_librosa,
            "soundfile": mock_soundfile,
            "sklearn": mock_sklearn,
            "sklearn.metrics": MagicMock(),
            "sklearn.metrics.pairwise": MagicMock(),
            "pydub": mock_pydub,
        }

        # Apply patches and reload module
        with patch.dict(sys.modules, mocks):
            if "src.services.audio_similarity_service" in sys.modules:
                del sys.modules["src.services.audio_similarity_service"]

            import src.services.audio_similarity_service

            importlib.reload(src.services.audio_similarity_service)

            service = src.services.audio_similarity_service.AudioSimilarityService()
            # Force availability
            service.available = True

            music_files = [
                {"path": "file1.mp3", "metadata": {}},
                {"path": "file2.mp3", "metadata": {"duration": 120.0}},
            ]

            # Mock compute_fingerprint
            with patch.object(service, "compute_fingerprint", return_value=None):
                service.find_duplicates(music_files)

            # Verify mutagen.File was called for file1.mp3 via our injected mock
            mock_mutagen.File.assert_any_call("file1.mp3")

        # Cleanup
        if "src.services.audio_similarity_service" in sys.modules:
            del sys.modules["src.services.audio_similarity_service"]

    def test_find_duplicates_missing_duration_skips_file(self):
        """Test that files without duration are skipped"""

        mock_mutagen = MagicMock()
        # Mock mutagen.File returning None
        mock_mutagen.File.return_value = None

        mocks = {
            "mutagen": mock_mutagen,
            "numpy": MagicMock(),
            "librosa": MagicMock(),
            "soundfile": MagicMock(),
            "sklearn": MagicMock(),
            "sklearn.metrics.pairwise": MagicMock(),
            "pydub": MagicMock(),
        }

        with patch.dict(sys.modules, mocks):
            if "src.services.audio_similarity_service" in sys.modules:
                del sys.modules["src.services.audio_similarity_service"]

            import src.services.audio_similarity_service

            importlib.reload(src.services.audio_similarity_service)

            service = src.services.audio_similarity_service.AudioSimilarityService()
            service.available = True

            music_files = [{"path": "file1.mp3", "metadata": {}}]

            # Mock logger
            with patch("src.services.audio_similarity_service.logger"):
                duplicates = service.find_duplicates(music_files)

            self.assertEqual(duplicates, [])

        # Cleanup
        if "src.services.audio_similarity_service" in sys.modules:
            del sys.modules["src.services.audio_similarity_service"]


if __name__ == "__main__":
    unittest.main()
