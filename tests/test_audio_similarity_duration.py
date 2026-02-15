
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock all dependencies
sys.modules['numpy'] = MagicMock()
sys.modules['mutagen'] = MagicMock()
sys.modules['librosa'] = MagicMock()
sys.modules['soundfile'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()

# Now import the service
from src.services.audio_similarity_service import AudioSimilarityService

class TestAudioSimilarityDuration(unittest.TestCase):
    def setUp(self):
        # We need to mock logger in the module before it's used
        self.service = AudioSimilarityService()
        self.service.available = True # Force availability for testing

    @patch('mutagen.File')
    def test_find_duplicates_duration_extraction(self, mock_mutagen_file):
        # Mock mutagen.File(path).info.length
        mock_audio = MagicMock()
        mock_audio.info.length = 120.5
        mock_mutagen_file.return_value = mock_audio

        music_files = [
            {'path': 'file1.mp3', 'metadata': {}},
            {'path': 'file2.mp3', 'metadata': {'duration': 120.0}} # Already has duration
        ]

        # We mock compute_fingerprint to avoid logic beyond duration extraction
        with patch.object(self.service, 'compute_fingerprint', return_value=None):
            self.service.find_duplicates(music_files)

        # Verify mutagen.File was called for file1.mp3 (no duration)
        mock_mutagen_file.assert_any_call('file1.mp3')

    @patch('mutagen.File')
    def test_find_duplicates_missing_duration_skips_file(self, mock_mutagen_file):
        # Mock mutagen.File returning None or missing info
        mock_mutagen_file.return_value = None

        music_files = [
            {'path': 'file1.mp3', 'metadata': {}}
        ]

        # Mock logger to avoid actual logging during test
        with patch('src.services.audio_similarity_service.logger') as mock_logger:
            duplicates = self.service.find_duplicates(music_files)

        self.assertEqual(duplicates, [])

if __name__ == '__main__':
    unittest.main()
