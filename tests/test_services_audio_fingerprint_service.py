"""
Tests for Audio Fingerprint Service
"""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestAudioFingerprintService(unittest.TestCase):
    def setUp(self):
        # Create a mock for acoustid
        self.mock_acoustid = MagicMock()

        # Patch sys.modules to inject our mock acoustid
        # We use patch.dict so it's undone after the test
        self.modules_patcher = patch.dict(sys.modules, {"acoustid": self.mock_acoustid})
        self.modules_patcher.start()

        # Import (or reload) the module under test so it picks up the mocked acoustid
        # We need to ensure we are testing the module with the mock injected
        import src.services.audio_fingerprint_service

        self.module = importlib.reload(src.services.audio_fingerprint_service)

        self.AudioFingerprinter = self.module.AudioFingerprinter
        self.DuplicateFinder = self.module.DuplicateFinder

    def tearDown(self):
        self.modules_patcher.stop()
        # Reload the module again to restore it to its original state (e.g. without the mock)
        # This ensures other tests don't see the effects of our injection
        if "src.services.audio_fingerprint_service" in sys.modules:
            import src.services.audio_fingerprint_service

            importlib.reload(src.services.audio_fingerprint_service)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_initialization_success(self, mock_check_tool):
        """Test initialization when dependencies are present."""
        # Setup HAS_ACOUSTID to True in the module
        # Note: Since we injected 'acoustid' into sys.modules, the reload in setUp
        # should have set HAS_ACOUSTID = True inside the module.
        mock_check_tool.return_value = "/usr/bin/fpcalc"

        fingerprinter = self.AudioFingerprinter()
        self.assertTrue(fingerprinter.has_dependencies)
        mock_check_tool.assert_called_with("fpcalc")

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_initialization_missing_module(self, mock_check_tool):
        """Test initialization when acoustid module is missing."""
        # To test missing module, we need to restart the setup without the mock in sys.modules
        self.modules_patcher.stop()

        # Ensure acoustid is NOT in sys.modules (if it is, remove it for this test)
        if "acoustid" in sys.modules:
            del sys.modules["acoustid"]

        # Capture real import before patching
        real_import = __import__

        def side_effect(name, *args, **kwargs):
            if name == "acoustid":
                raise ImportError("No module named acoustid")
            return real_import(name, *args, **kwargs)

        # We also need to prevent it from being imported if it actually exists on the system
        with patch.dict(sys.modules):
            with patch("builtins.__import__", side_effect=side_effect):
                # Reload module to trigger ImportError block
                import src.services.audio_fingerprint_service

                self.module = importlib.reload(src.services.audio_fingerprint_service)
                self.AudioFingerprinter = self.module.AudioFingerprinter

                mock_check_tool.return_value = "/usr/bin/fpcalc"

                fingerprinter = self.AudioFingerprinter()
                self.assertFalse(fingerprinter.has_dependencies)

        # Restore patcher for tearDown
        self.modules_patcher.start()
        # Restore module state
        import src.services.audio_fingerprint_service

        self.module = importlib.reload(src.services.audio_fingerprint_service)
        self.AudioFingerprinter = self.module.AudioFingerprinter

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_initialization_missing_tool(self, mock_check_tool):
        """Test initialization when fpcalc tool is missing."""
        mock_check_tool.return_value = None

        fingerprinter = self.AudioFingerprinter()
        self.assertFalse(fingerprinter.has_dependencies)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_generate_fingerprint_success(self, mock_check_tool):
        """Test generating fingerprint successfully."""
        mock_check_tool.return_value = "/path/to/fpcalc"
        self.mock_acoustid.fingerprint_file.return_value = (120.5, "test_fingerprint")

        fingerprinter = self.AudioFingerprinter()
        result = fingerprinter.generate_fingerprint("song.mp3")

        self.assertEqual(result, (120.5, "test_fingerprint"))
        self.mock_acoustid.fingerprint_file.assert_called_with("song.mp3")

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_generate_fingerprint_error(self, mock_check_tool):
        """Test generating fingerprint with error."""
        mock_check_tool.return_value = "/path/to/fpcalc"
        self.mock_acoustid.fingerprint_file.side_effect = Exception("File error")

        fingerprinter = self.AudioFingerprinter()
        result = fingerprinter.generate_fingerprint("bad.mp3")

        self.assertIsNone(result)

    @patch("src.services.audio_fingerprint_service.DependencyChecker.check_system_tool")
    def test_find_duplicates(self, mock_check_tool):
        """Test finding duplicates."""
        mock_check_tool.return_value = "/path/to/fpcalc"

        finder = self.DuplicateFinder()
        # Ensure dependencies are marked as present
        finder.fingerprinter.has_dependencies = True

        with patch.object(finder.fingerprinter, "generate_fingerprint") as mock_gen:
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
    def test_find_duplicates_missing_deps(self, mock_check_tool):
        """Test finding duplicates when dependencies are missing."""
        # Re-using the logic from test_initialization_missing_module is a bit complex
        # Instead, we can just patch HAS_ACOUSTID on the already loaded module
        mock_check_tool.return_value = "/path/to/fpcalc"

        with patch("src.services.audio_fingerprint_service.HAS_ACOUSTID", False):
            # We also need to re-init AudioFingerprinter to pick up the flag
            # But the flag is used in __init__ via self._check_dependencies
            # self._check_dependencies uses the global HAS_ACOUSTID

            # Since we modify the global in the module, instances created afterwards should see it

            finder = self.DuplicateFinder()
            # However, the module object 'src.services.audio_fingerprint_service'
            # is what we have in self.module

            # Let's verify HAS_ACOUSTID is False
            # We patched it using string path, which patches it on the module

            # finder.fingerprinter created in __init__
            self.assertFalse(finder.fingerprinter.has_dependencies)

            files = ["file1.mp3", "file2.mp3"]
            duplicates = finder.find_duplicates(files)

            self.assertEqual(duplicates, {})
