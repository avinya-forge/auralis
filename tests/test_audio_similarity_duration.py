import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies strictly before importing service
# This ensures consistency regardless of installed packages
mock_modules = [
    "numpy",
    "mutagen",
    "librosa",
    "soundfile",
    "sklearn",
    "sklearn.metrics.pairwise",
    "pydub"
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Now import the service
from src.services.audio_similarity_service import AudioSimilarityService  # noqa: E402


class TestAudioSimilarityDuration(unittest.TestCase):
    def setUp(self):
        self.service = AudioSimilarityService()
        self.service.available = True

    def test_find_duplicates_duration_extraction(self):
        """Test that duration is extracted using mutagen if missing from metadata"""
        # Setup mocks
        mock_audio = MagicMock()
        mock_audio.info.length = 120.5

        # We need to patch the mutagen.File that the service imported
        # Since we mocked sys.modules['mutagen'], the service has that Mock object.
        # We can configure that Mock object directly.
        sys.modules["mutagen"].File.return_value = mock_audio

        music_files = [
            {"path": "file1.mp3", "metadata": {}},
            {"path": "file2.mp3", "metadata": {"duration": 120.0}},
        ]

        # Mock compute_fingerprint to avoid logic beyond duration extraction
        with patch.object(self.service, "compute_fingerprint", return_value=None):
            self.service.find_duplicates(music_files)

        # Verify mutagen.File was called for file1.mp3
        sys.modules["mutagen"].File.assert_any_call("file1.mp3")

    def test_find_duplicates_missing_duration_skips_file(self):
        """Test that files without duration are skipped"""
        # Mock mutagen.File returning None (simulation of failure/no audio)
        sys.modules["mutagen"].File.return_value = None

        music_files = [{"path": "file1.mp3", "metadata": {}}]

        # Mock logger
        with patch("src.services.audio_similarity_service.logger"):
            duplicates = self.service.find_duplicates(music_files)

        self.assertEqual(duplicates, [])


if __name__ == "__main__":
    unittest.main()
