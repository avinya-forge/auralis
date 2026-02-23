"""
Tests for AudioAnalysisService
"""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

# Mock dependencies
mock_librosa = MagicMock()
mock_librosa.beat = MagicMock()
mock_librosa.feature = MagicMock()


# Mock Mutagen
class MockMP3(MagicMock):
    pass


class MockFLAC(MagicMock):
    pass


class MockID3(MagicMock):
    pass


class MockOgg(MagicMock):
    pass


mock_mp3 = MagicMock()
mock_mp3.MP3 = MockMP3

mock_flac = MagicMock()
mock_flac.FLAC = MockFLAC

mock_id3 = MagicMock()
mock_id3.TBPM = MagicMock()
mock_id3.TKEY = MagicMock()
mock_id3.TMOO = MagicMock()

mock_ogg = MagicMock()
mock_ogg.OggVorbis = MockOgg

mock_mutagen = MagicMock()
mock_mutagen.mp3 = mock_mp3
mock_mutagen.flac = mock_flac
mock_mutagen.id3 = mock_id3
mock_mutagen.ogg = mock_ogg
mock_mutagen.File = MagicMock()


class TestAudioAnalysisService(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules to mock librosa and mutagen
        # We assume numpy is real and installed in the env
        self.module_patcher = patch.dict(sys.modules, {
            "librosa": mock_librosa,
            "mutagen": mock_mutagen,
            "mutagen.mp3": mock_mp3,
            "mutagen.flac": mock_flac,
            "mutagen.id3": mock_id3,
            "mutagen.ogg": mock_ogg,
            "numpy": np
        })
        self.module_patcher.start()

        # Reload module under test
        if "src.services.audio_analysis_service" in sys.modules:
            import src.services.audio_analysis_service
            importlib.reload(src.services.audio_analysis_service)
        else:
            import src.services.audio_analysis_service

        self.module = src.services.audio_analysis_service
        self.analyzer = self.module.AudioAnalyzer()

        # Reset mocks
        mock_librosa.reset_mock()
        mock_mutagen.reset_mock()
        mock_mutagen.File.reset_mock()
        # mock_id3.TBPM etc are instances of MagicMock, reset them
        mock_id3.TBPM.reset_mock()
        mock_id3.TKEY.reset_mock()
        mock_id3.TMOO.reset_mock()

        mock_librosa.load.side_effect = None
        mock_librosa.beat.beat_track.side_effect = None

    def tearDown(self):
        self.module_patcher.stop()
        if "src.services.audio_analysis_service" in sys.modules:
            import src.services.audio_analysis_service
            importlib.reload(src.services.audio_analysis_service)

    def test_init(self):
        """Test initialization"""
        with patch("src.services.audio_analysis_service.logger") as mock_logger:
            self.module.AudioAnalyzer()
            mock_logger.warning.assert_not_called()

        # Test with missing dependencies
        with patch.dict(sys.modules):
            sys.modules["librosa"] = None
            with patch("src.services.audio_analysis_service.logger") as mock_logger:
                self.module.AudioAnalyzer()
                mock_logger.warning.assert_called_with(
                    "Librosa or numpy not installed. Audio analysis will not work."
                )

    def test_get_bpm_success(self):
        """Test successful BPM detection"""
        # If numpy is mocked, we need special handling if beat_track returns mock
        if isinstance(np, MagicMock):
            mock_librosa.load.return_value = (MagicMock(), 22050)
            # Scalar return
            mock_librosa.beat.beat_track.return_value = (120.0, MagicMock())
        else:
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            mock_librosa.beat.beat_track.return_value = (120.0, np.array([10, 20]))

        bpm = self.analyzer.get_bpm("/path/to/file.mp3")

        self.assertEqual(bpm, 120.0)
        mock_librosa.load.assert_called_with("/path/to/file.mp3", sr=None, duration=60)
        mock_librosa.beat.beat_track.assert_called()

    def test_get_bpm_no_librosa(self):
        """Test BPM detection without librosa"""
        with patch.dict(sys.modules):
            sys.modules["librosa"] = None
            bpm = self.analyzer.get_bpm("/path/to/file.mp3")
            self.assertIsNone(bpm)

    def test_get_bpm_error(self):
        """Test BPM detection error"""
        mock_librosa.load.side_effect = Exception("Load error")

        bpm = self.analyzer.get_bpm("/path/to/file.mp3")

        self.assertIsNone(bpm)

    def test_get_bpm_array_return(self):
        """Test BPM detection when beat_track returns an array"""
        if isinstance(np, MagicMock):
            # Handle mocked numpy
            # We need return value to be an instance of np.ndarray and behave like float
            class FloatArray(np.ndarray):
                def __float__(self):
                    return 120.0

                def __getitem__(self, idx):
                    return 120.0

                @property
                def size(self):
                    return 1

            mock_array = FloatArray()
            mock_librosa.load.return_value = (MagicMock(), 22050)
            mock_librosa.beat.beat_track.return_value = (mock_array, MagicMock())
        else:
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            mock_librosa.beat.beat_track.return_value = (
                np.array([120.0]),
                np.array([10, 20]),
            )

        bpm = self.analyzer.get_bpm("/path/to/file.mp3")

        self.assertEqual(bpm, 120.0)

    def test_get_key_success(self):
        """Test successful Key detection"""
        if isinstance(np, MagicMock):
            return

        mock_librosa.load.return_value = (np.zeros(100), 22050)
        mock_chroma = np.zeros((12, 10))
        mock_chroma[0, :] = 1.0  # C
        mock_chroma[4, :] = 1.0  # E
        mock_chroma[7, :] = 1.0  # G

        mock_librosa.feature.chroma_cqt.return_value = mock_chroma

        key = self.analyzer.get_key("/path/to/file.mp3")

        self.assertEqual(key, "C Major")

    def test_get_key_minor(self):
        """Test successful A Minor detection"""
        if isinstance(np, MagicMock):
            return

        mock_librosa.load.return_value = (np.zeros(100), 22050)
        mock_chroma = np.zeros((12, 10))
        mock_chroma[9, :] = 1.0  # A
        mock_chroma[0, :] = 1.0  # C
        mock_chroma[4, :] = 1.0  # E

        mock_librosa.feature.chroma_cqt.return_value = mock_chroma

        key = self.analyzer.get_key("/path/to/file.mp3")

        self.assertEqual(key, "A Minor")

    def test_get_mood(self):
        """Test mood detection heuristic"""
        self.assertEqual(self.analyzer.get_mood(130, "C Major"), "Energetic")
        self.assertEqual(self.analyzer.get_mood(80, "C Major"), "Calm")
        self.assertEqual(self.analyzer.get_mood(130, "A Minor"), "Intense")
        self.assertEqual(self.analyzer.get_mood(100, "A Minor"), "Melancholic")
        self.assertEqual(self.analyzer.get_mood(None, "C Major"), "Unknown")
        self.assertEqual(self.analyzer.get_mood(120, None), "Unknown")

    def test_save_analysis_tags_mp3(self):
        """Test saving tags to MP3"""
        mock_audio = MockMP3()
        mock_mutagen.File.return_value = mock_audio

        with patch("src.services.audio_analysis_service.HAS_MUTAGEN", True):
            success = self.analyzer.save_analysis_tags("test.mp3", 120.5, "C Major", "Energetic")

            self.assertTrue(success)
            mock_mutagen.File.assert_called_with("test.mp3")

            mock_audio.save.assert_called()

            mock_id3.TBPM.assert_called()
            mock_id3.TKEY.assert_called()
            mock_id3.TMOO.assert_called()

    def test_save_analysis_tags_flac(self):
        """Test saving tags to FLAC"""
        mock_audio = MockFLAC()
        mock_mutagen.File.return_value = mock_audio

        with patch("src.services.audio_analysis_service.HAS_MUTAGEN", True):
            success = self.analyzer.save_analysis_tags("test.flac", 120.5, "C Major", "Energetic")

            self.assertTrue(success)
            mock_audio.save.assert_called()


if __name__ == "__main__":
    unittest.main()
