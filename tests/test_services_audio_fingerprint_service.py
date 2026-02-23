"""
Tests for Audio Fingerprint Service
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Create a mock for acoustid
mock_acoustid = MagicMock()
sys.modules["acoustid"] = mock_acoustid

# Now import the module under test
from src.services.audio_fingerprint_service import AudioFingerprinter, DuplicateFinder  # noqa: E402


class TestAudioFingerprintService(unittest.TestCase):
    def setUp(self):
        self.mock_acoustid = mock_acoustid
        # Reset mock
        self.mock_acoustid.reset_mock()
        # Reset side_effect and return_value to avoid leaks
        self.mock_acoustid.fingerprint_file.side_effect = None
        self.mock_acoustid.fingerprint_file.return_value = None

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", True)
    def test_initialization_success(self, mock_check_tool):
        """Test initialization when dependencies are present."""
        mock_check_tool.return_value = "/usr/bin/fpcalc"

        fingerprinter = AudioFingerprinter()
        self.assertTrue(fingerprinter.has_dependencies)
        mock_check_tool.assert_called_with("fpcalc")

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", False)
    def test_initialization_missing_module(self, mock_check_tool):
        """Test initialization when acoustid module is missing."""
        mock_check_tool.return_value = "/usr/bin/fpcalc"

        fingerprinter = AudioFingerprinter()
        self.assertFalse(fingerprinter.has_dependencies)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", True)
    def test_initialization_missing_tool(self, mock_check_tool):
        """Test initialization when fpcalc tool is missing."""
        mock_check_tool.return_value = None

        fingerprinter = AudioFingerprinter()
        self.assertFalse(fingerprinter.has_dependencies)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", True)
    def test_generate_fingerprint_success(self, mock_check_tool):
        """Test generating fingerprint successfully."""
        mock_check_tool.return_value = "/path/to/fpcalc"
        self.mock_acoustid.fingerprint_file.return_value = (120.5, "test_fingerprint")

        fingerprinter = AudioFingerprinter()
        result = fingerprinter.generate_fingerprint("song.mp3")

        self.assertEqual(result, (120.5, "test_fingerprint"))
        self.mock_acoustid.fingerprint_file.assert_called_with("song.mp3")

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", True)
    def test_generate_fingerprint_error(self, mock_check_tool):
        """Test generating fingerprint with error."""
        mock_check_tool.return_value = "/path/to/fpcalc"
        self.mock_acoustid.fingerprint_file.side_effect = Exception("File error")

        fingerprinter = AudioFingerprinter()
        result = fingerprinter.generate_fingerprint("bad.mp3")

        self.assertIsNone(result)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", True)
    def test_find_duplicates(self, mock_check_tool):
        """Test finding duplicates."""
        mock_check_tool.return_value = "/path/to/fpcalc"

        finder = DuplicateFinder()
        # Ensure dependencies are marked as present
        finder.fingerprinter.has_dependencies = True

        with patch.object(finder.fingerprinter, 'generate_fingerprint') as mock_gen:
            mock_gen.side_effect = [
                (100.0, "fp1"),  # file1
                (100.0, "fp2"),  # file2 (unique)
                (100.0, "fp1"),  # file3 (duplicate of file1)
            ]

            files = ["file1.mp3", "file2.mp3", "file3.mp3"]
            duplicates = finder.find_duplicates(files)

            self.assertIn("fp1", duplicates)
            self.assertEqual(len(duplicates["fp1"]), 2)
            self.assertIn("file1.mp3", duplicates["fp1"])
            self.assertIn("file3.mp3", duplicates["fp1"])
            self.assertNotIn("fp2", duplicates)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    @patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", False)
    def test_find_duplicates_missing_deps(self, mock_check_tool):
        """Test finding duplicates when dependencies are missing."""
        mock_check_tool.return_value = "/path/to/fpcalc"

        finder = DuplicateFinder()
        # Ensure dependencies are marked as missing (should be false from init if HAS_ACOUSTID is False)
        # But we double check
        self.assertFalse(finder.fingerprinter.has_dependencies)

        files = ["file1.mp3", "file2.mp3"]
        duplicates = finder.find_duplicates(files)

        self.assertEqual(duplicates, {})
