import sys
import unittest
from unittest.mock import MagicMock

# Create mocks for optional dependencies before importing the module under test
# This ensures that even if the module imports them at top level (which it doesn't for pydub), we control them.
sys.modules["pydub"] = MagicMock()
sys.modules["mutagen"] = MagicMock()
sys.modules["mutagen.mp3"] = MagicMock()
sys.modules["mutagen.flac"] = MagicMock()
sys.modules["mutagen.ogg"] = MagicMock()
sys.modules["mutagen.id3"] = MagicMock()

from src.services.audio_analysis_service import AudioAnalyzer  # noqa: E402


class TestReplayGain(unittest.TestCase):
    def setUp(self):
        self.analyzer = AudioAnalyzer()
        # Reset mocks
        pydub_mock = sys.modules["pydub"]
        pydub_mock.reset_mock()
        pydub_mock.AudioSegment.from_file.side_effect = None

    def test_calculate_replay_gain_success(self):
        # Setup mock for pydub.AudioSegment
        mock_audio = MagicMock()
        mock_audio.dBFS = -20.0

        # Since we patched sys.modules['pydub'], the import inside the method will return that mock.
        pydub_mock = sys.modules["pydub"]
        pydub_mock.AudioSegment.from_file.return_value = mock_audio

        gain = self.analyzer.calculate_replay_gain("test.mp3", target_dbfs=-14.0)

        self.assertEqual(gain, 6.0)
        pydub_mock.AudioSegment.from_file.assert_called_with("test.mp3")

    def test_calculate_replay_gain_error(self):
        pydub_mock = sys.modules["pydub"]
        pydub_mock.AudioSegment.from_file.side_effect = Exception("File error")

        gain = self.analyzer.calculate_replay_gain("bad.mp3")
        self.assertIsNone(gain)

    def test_save_replay_gain_tags_mp3(self):
        mutagen_mock = sys.modules["mutagen"]
        mock_file = MagicMock()
        # Mock isinstance check
        mutagen_mock.mp3.MP3 = type("MP3", (), {})
        mock_file.__class__ = mutagen_mock.mp3.MP3
        mutagen_mock.File.return_value = mock_file

        # We need HAS_MUTAGEN to be True.
        # It is set at module level import time.
        # Since we mocked mutagen before import, it should be True.

        success = self.analyzer.save_replay_gain_tags("test.mp3", 6.0)

        self.assertTrue(success)
        mock_file.save.assert_called_once()

    def test_save_replay_gain_tags_flac(self):
        mutagen_mock = sys.modules["mutagen"]
        mock_file = MagicMock()
        mock_file.__class__ = mutagen_mock.flac.FLAC  # type("FLAC", (), {})
        # Ensure it behaves like a dict for item assignment
        mock_file.__setitem__ = MagicMock()

        mutagen_mock.File.return_value = mock_file
        # Mock isinstance
        mutagen_mock.mp3.MP3 = type("MP3", (), {})
        mutagen_mock.flac.FLAC = type("FLAC", (), {})
        mock_file.__class__ = mutagen_mock.flac.FLAC

        success = self.analyzer.save_replay_gain_tags("test.flac", 3.5)

        self.assertTrue(success)
        mock_file.__setitem__.assert_called_with("REPLAYGAIN_TRACK_GAIN", "3.50 dB")
        mock_file.save.assert_called_once()
