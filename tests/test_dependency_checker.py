import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

from src.utils.dependency_checker import DependencyChecker


class TestDependencyChecker(unittest.TestCase):
    def setUp(self):
        self.checker = DependencyChecker()

    @patch("importlib.import_module")
    def test_check_module_installed(self, mock_import):
        """Test check_module returns True when module is importable"""
        mock_import.return_value = MagicMock()
        self.assertTrue(self.checker.check_module("os"))

    @patch("importlib.import_module")
    def test_check_module_not_installed(self, mock_import):
        """Test check_module returns False when module is missing"""
        mock_import.side_effect = ImportError("No module named 'fake_module'")
        self.assertFalse(self.checker.check_module("fake_module"))

    @patch("shutil.which")
    def test_check_system_tool_installed(self, mock_which):
        """Test check_system_tool returns path when tool is found"""
        mock_which.return_value = "/usr/bin/ffmpeg"
        self.assertEqual(self.checker.check_system_tool("ffmpeg"), "/usr/bin/ffmpeg")

    @patch("shutil.which")
    def test_check_system_tool_not_installed(self, mock_which):
        """Test check_system_tool returns None when tool is missing"""
        mock_which.return_value = None
        self.assertIsNone(self.checker.check_system_tool("missing_tool"))

    @patch("ctypes.util.find_library")
    def test_check_library_installed(self, mock_find):
        """Test check_library returns path when library is found"""
        mock_find.return_value = "libsndfile.so.1"
        self.assertEqual(self.checker.check_library("sndfile"), "libsndfile.so.1")

    @patch("ctypes.util.find_library")
    def test_check_library_not_installed(self, mock_find):
        """Test check_library returns None when library is missing"""
        mock_find.return_value = None
        self.assertIsNone(self.checker.check_library("missing_lib"))

    @patch("src.utils.dependency_checker.DependencyChecker.check_module")
    @patch("src.utils.dependency_checker.DependencyChecker.check_system_tool")
    @patch("platform.system")
    def test_check_all(self, mock_platform, mock_check_tool, mock_check_module):
        """Test check_all returns comprehensive report"""
        mock_platform.return_value = "Linux"
        mock_check_module.return_value = True
        mock_check_tool.return_value = "/usr/bin/ffmpeg"

        report = self.checker.check_all()

        self.assertEqual(report["platform"], "Linux")
        self.assertTrue(report["core"]["PyQt6"])
        self.assertTrue(report["audio_similarity"]["librosa"])
        self.assertEqual(report["system_tools"]["ffmpeg"]["path"], "/usr/bin/ffmpeg")

    def test_get_install_instructions(self):
        """Test get_install_instructions generates correct instructions"""
        missing_modules = ["sklearn", "pyaudio"]
        missing_tools = ["ffmpeg"]
        instructions = self.checker.get_install_instructions(missing_modules, missing_tools)

        self.assertIn("pip install", instructions)
        self.assertIn("scikit-learn", instructions)  # Check mapping
        self.assertIn("pyaudio", instructions)

        if sys.platform.startswith("linux"):
            self.assertIn("sudo apt-get install", instructions)
            self.assertIn("ffmpeg", instructions)

    @patch("subprocess.check_call")
    def test_install_pip_packages_success(self, mock_check_call):
        """Test install_pip_packages success"""
        self.assertTrue(self.checker.install_pip_packages(["package"]))
        mock_check_call.assert_called()

    @patch("subprocess.check_call")
    def test_install_pip_packages_failure(self, mock_check_call):
        """Test install_pip_packages failure"""
        mock_check_call.side_effect = subprocess.CalledProcessError(1, "cmd")
        self.assertFalse(self.checker.install_pip_packages(["package"]))

if __name__ == "__main__":
    unittest.main()
