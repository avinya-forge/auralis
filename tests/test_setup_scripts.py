"""
Unit tests for setup scripts (audio similarity and language detection)
"""

import os
import sys
import unittest
from unittest.mock import patch

import setup_audio_similarity
import setup_language_detection

# Ensure root directory is in sys.path
sys.path.append(os.getcwd())


class TestSetupAudioSimilarity(unittest.TestCase):

    @patch("setup_audio_similarity.DependencyChecker")
    @patch("builtins.print")
    def test_install_dependencies_success(self, mock_print, MockChecker):
        """Test successful dependency installation"""
        checker_instance = MockChecker.return_value
        checker_instance.install_pip_packages.return_value = True

        with patch("platform.system", return_value="Linux"):
            result = setup_audio_similarity.install_dependencies()

        self.assertTrue(result)
        checker_instance.install_pip_packages.assert_called()

    @patch("setup_audio_similarity.DependencyChecker")
    @patch("builtins.print")
    def test_install_dependencies_failure(self, mock_print, MockChecker):
        """Test failed dependency installation"""
        checker_instance = MockChecker.return_value
        checker_instance.install_pip_packages.return_value = False

        result = setup_audio_similarity.install_dependencies()

        self.assertFalse(result)

    @patch("setup_audio_similarity.DependencyChecker")
    @patch("builtins.print")
    def test_check_system_dependencies(self, mock_print, MockChecker):
        """Test system dependency check"""
        checker_instance = MockChecker.return_value
        checker_instance.check_all.return_value = {
            "system_tools": {"ffmpeg": {"installed": True, "path": "/bin/ffmpeg"}},
            "libraries": {"sndfile": {"installed": True, "path": "/lib/sndfile"}},
        }

        with patch("platform.system", return_value="Linux"):
            setup_audio_similarity.check_system_dependencies()

        # Verify output (checking print calls is tedious, just ensure it runs)
        mock_print.assert_called()

    @patch("setup_audio_similarity.DependencyChecker")
    @patch("builtins.print")
    def test_test_dependencies(self, mock_print, MockChecker):
        """Test dependency testing"""
        checker_instance = MockChecker.return_value
        checker_instance.check_all.return_value = {
            "audio_similarity": {"librosa": True, "numpy": True}
        }
        checker_instance.check_audio_capabilities.return_value = {"success": True, "message": "OK"}

        result = setup_audio_similarity.test_dependencies()
        self.assertTrue(result)


class TestSetupLanguageDetection(unittest.TestCase):

    @patch("setup_language_detection.DependencyChecker")
    @patch("builtins.print")
    def test_install_dependencies_linux(self, mock_print, MockChecker):
        """Test installation on Linux"""
        checker_instance = MockChecker.return_value
        checker_instance.install_pip_packages.return_value = True

        with patch("platform.system", return_value="Linux"):
            result = setup_language_detection.install_dependencies()

        self.assertTrue(result)
        # Verify pyaudio installation attempt
        # Original code: if checker.install_pip_packages(packages): ... then install pyaudio
        self.assertEqual(checker_instance.install_pip_packages.call_count, 2)

    @patch("setup_language_detection.DependencyChecker")
    @patch("builtins.print")
    def test_install_dependencies_windows(self, mock_print, MockChecker):
        """Test installation on Windows"""
        checker_instance = MockChecker.return_value
        checker_instance.install_pip_packages.return_value = True

        with patch("platform.system", return_value="Windows"):
            result = setup_language_detection.install_dependencies()

        self.assertTrue(result)
        # Windows tries to install pyaudio too
        self.assertEqual(checker_instance.install_pip_packages.call_count, 2)

    @patch("setup_language_detection.DependencyChecker")
    @patch("builtins.print")
    def test_test_dependencies(self, mock_print, MockChecker):
        """Test dependency testing"""
        checker_instance = MockChecker.return_value
        checker_instance.check_all.return_value = {"language_detection": {"langdetect": True}}

        result = setup_language_detection.test_dependencies()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
