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


class TestAudioAnalysisService(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules
        self.module_patcher = patch.dict(sys.modules, {"librosa": mock_librosa})
        self.module_patcher.start()

        # Reload module under test
        if "src.services.audio_analysis_service" in sys.modules:
            import src.services.audio_analysis_service

            importlib.reload(src.services.audio_analysis_service)
        else:
            import src.services.audio_analysis_service

        self.module = src.services.audio_analysis_service
        self.analyzer = self.module.AudioAnalyzer()

        # Reset mocks and clear side effects
        mock_librosa.reset_mock()
        mock_librosa.beat.reset_mock()
        mock_librosa.feature.reset_mock()
        mock_librosa.load.side_effect = None
        mock_librosa.beat.beat_track.side_effect = None
        mock_librosa.feature.chroma_cqt.side_effect = None

    def tearDown(self):
        self.module_patcher.stop()
        # Reload to restore original state
        if "src.services.audio_analysis_service" in sys.modules:
            import src.services.audio_analysis_service

            importlib.reload(src.services.audio_analysis_service)

    def test_init(self):
        """Test initialization"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            self.module.AudioAnalyzer()
            # Should not log warning (need to mock logger to verify)

        with patch("src.services.audio_analysis_service.HAS_LIBROSA", False):
            with patch("src.services.audio_analysis_service.logger") as mock_logger:
                self.module.AudioAnalyzer()
                mock_logger.warning.assert_called_with(
                    "Librosa not installed. Audio analysis will not work."
                )

    def test_get_bpm_success(self):
        """Test successful BPM detection"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            mock_librosa.beat.beat_track.return_value = (120.0, np.array([10, 20]))

            bpm = self.analyzer.get_bpm("/path/to/file.mp3")

            self.assertEqual(bpm, 120.0)
            mock_librosa.load.assert_called_with("/path/to/file.mp3", sr=None, duration=60)
            mock_librosa.beat.beat_track.assert_called()

    def test_get_bpm_no_librosa(self):
        """Test BPM detection without librosa"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", False):
            bpm = self.analyzer.get_bpm("/path/to/file.mp3")
            self.assertIsNone(bpm)

    def test_get_bpm_error(self):
        """Test BPM detection error"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.side_effect = Exception("Load error")

            bpm = self.analyzer.get_bpm("/path/to/file.mp3")

            self.assertIsNone(bpm)

    def test_get_bpm_array_return(self):
        """Test BPM detection when beat_track returns an array"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            # Simulate returning a 1-element array
            mock_librosa.beat.beat_track.return_value = (
                np.array([120.0]),
                np.array([10, 20]),
            )

            bpm = self.analyzer.get_bpm("/path/to/file.mp3")

            self.assertEqual(bpm, 120.0)

    def test_get_key_success(self):
        """Test successful Key detection"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            # Mock chroma: 12 bins, 10 frames
            mock_chroma = np.zeros((12, 10))
            # Set strong C major components (indices 0, 4, 7) for C, E, G
            mock_chroma[0, :] = 1.0  # C
            mock_chroma[4, :] = 1.0  # E
            mock_chroma[7, :] = 1.0  # G

            mock_librosa.feature.chroma_cqt.return_value = mock_chroma

            key = self.analyzer.get_key("/path/to/file.mp3")

            # With equal weights on C, E, G, it should be C Major.
            self.assertEqual(key, "C Major")

            mock_librosa.load.assert_called()
            mock_librosa.feature.chroma_cqt.assert_called()

    def test_get_key_minor(self):
        """Test successful A Minor detection"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            # Mock chroma: 12 bins, 10 frames
            mock_chroma = np.zeros((12, 10))
            # A Minor: A, C, E -> 9, 0, 4
            mock_chroma[9, :] = 1.0  # A
            mock_chroma[0, :] = 1.0  # C
            mock_chroma[4, :] = 1.0  # E

            mock_librosa.feature.chroma_cqt.return_value = mock_chroma

            key = self.analyzer.get_key("/path/to/file.mp3")

            self.assertEqual(key, "A Minor")

    def test_get_key_no_librosa(self):
        """Test Key detection without librosa"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", False):
            key = self.analyzer.get_key("/path/to/file.mp3")
            self.assertIsNone(key)

    def test_get_key_error(self):
        """Test Key detection error"""
        with patch("src.services.audio_analysis_service.HAS_LIBROSA", True):
            mock_librosa.load.side_effect = Exception("Load error")

            key = self.analyzer.get_key("/path/to/file.mp3")

            self.assertIsNone(key)


if __name__ == "__main__":
    unittest.main()
