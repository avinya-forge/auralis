"""
Tests for CLI Main Module
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(".")  # noqa: E402

from src.cli.cli_main import ConsoleHandler, run_cli  # noqa: E402

# Import MetadataService to ensure it's loaded for patching
from src.services.metadata_service import MetadataService  # noqa: F401, E402


class TestCLI(unittest.TestCase):
    """Test CLI functionality"""

    def setUp(self):
        # Mock QCoreApplication to avoid issues
        self.app_patcher = patch("src.cli.cli_main.QCoreApplication")
        self.mock_app = self.app_patcher.start()

    def tearDown(self):
        self.app_patcher.stop()

    @patch("src.core.scanner.MusicScanner")
    def test_scan_command(self, mock_scanner_cls):
        """Test scan command"""
        # Setup mock
        scanner = mock_scanner_cls.return_value
        scanner.scan_directories.return_value = [{"path": "test.mp3"}]

        # Signals
        scanner.progress_updated = MagicMock()
        scanner.file_scanned = MagicMock()

        # Run CLI
        test_args = ["cli_main.py", "scan", "test_dir", "--depth", "5"]
        with patch.object(sys, "argv", test_args):
            run_cli()

        # Verify
        mock_scanner_cls.assert_called_once()
        scanner.scan_directories.assert_called_once()
        args, kwargs = scanner.scan_directories.call_args
        # args[0] is directories, args[1] is options
        self.assertEqual(args[0], ["test_dir"])
        self.assertEqual(args[1]["max_scan_depth"], 5)

        # Verify signals connected
        scanner.progress_updated.connect.assert_called()
        scanner.file_scanned.connect.assert_called()

    @patch("src.core.organizer.MusicOrganizer")
    @patch("src.cli.cli_main._load_files")
    def test_organize_command(self, mock_load_files, mock_organizer_cls):
        """Test organize command"""
        # Setup mock
        organizer = mock_organizer_cls.return_value
        organizer.organize_files.return_value = {"total_files": 1, "organized_files": 1}

        # Signals
        organizer.progress_updated = MagicMock()
        organizer.file_organized = MagicMock()

        # Mock load files
        mock_load_files.return_value = [{"path": "test.mp3"}]

        # Run CLI
        test_args = [
            "cli_main.py",
            "organize",
            "source_dir",
            "dest_dir",
            "--dry-run",
            "--no-rename",
        ]
        with patch.object(sys, "argv", test_args):
            run_cli()

        # Verify
        mock_load_files.assert_called_with("source_dir")
        mock_organizer_cls.assert_called_with(dry_run=True)
        organizer.organize_files.assert_called_once()

        # Check options
        args, kwargs = organizer.organize_files.call_args
        # args[0] files, args[1] dest, args[2] options
        self.assertEqual(args[1], "dest_dir")
        self.assertEqual(args[2]["rename_files"], False)
        self.assertEqual(args[2]["organize_by_language"], True)  # Default

    @patch("src.core.organizer.MusicOrganizer")
    @patch("src.cli.cli_main._load_files")
    def test_organize_command_with_template(self, mock_load_files, mock_organizer_cls):
        """Test organize command with template"""
        # Setup mock
        organizer = mock_organizer_cls.return_value
        organizer.organize_files.return_value = {"total_files": 1, "organized_files": 1}
        organizer.progress_updated = MagicMock()
        organizer.file_organized = MagicMock()
        mock_load_files.return_value = [{"path": "test.mp3"}]

        # Run CLI
        test_args = [
            "cli_main.py",
            "organize",
            "source_dir",
            "dest_dir",
            "--template",
            "{artist}/{title}",
        ]
        with patch.object(sys, "argv", test_args):
            run_cli()

        # Verify options
        args, kwargs = organizer.organize_files.call_args
        options = args[2]
        self.assertEqual(options["directory_template"], "{artist}/{title}")

    @patch("src.services.metadata_service.MetadataService")
    @patch("src.cli.cli_main._load_files")
    def test_metadata_command(self, mock_load_files, mock_metadata_cls):
        """Test metadata command"""
        # Setup mock
        service = mock_metadata_cls.return_value
        service.update_metadata.return_value = [{"path": "test.mp3", "metadata": {}}]

        # Signals
        service.progress_updated = MagicMock()
        service.file_updated = MagicMock()

        # Mock load files
        mock_load_files.return_value = [{"path": "test.mp3"}]

        # Run CLI
        test_args = ["cli_main.py", "metadata", "source_dir", "--no-musicbrainz", "--force"]
        with patch.object(sys, "argv", test_args):
            run_cli()

        # Verify
        service.update_metadata.assert_called_once()
        args, kwargs = service.update_metadata.call_args
        # args[0] files, args[1] options
        options = args[1]
        self.assertEqual(options["use_musicbrainz"], False)
        self.assertEqual(options["use_discogs"], True)  # Default
        self.assertEqual(options["force_update"], True)

    @patch("src.services.metadata_service.MetadataService")
    @patch("src.cli.cli_main._load_files")
    def test_metadata_command_with_cover_art(self, mock_load_files, mock_metadata_cls):
        """Test metadata command with cover art"""
        # Setup mock
        service = mock_metadata_cls.return_value
        service.update_metadata.return_value = [{"path": "test.mp3", "metadata": {}}]
        service.progress_updated = MagicMock()
        service.file_updated = MagicMock()
        mock_load_files.return_value = [{"path": "test.mp3"}]

        # Run CLI
        test_args = ["cli_main.py", "metadata", "source_dir", "--fetch-cover-art"]
        with patch.object(sys, "argv", test_args):
            run_cli()

        # Verify options
        args, kwargs = service.update_metadata.call_args
        options = args[1]
        self.assertEqual(options["fetch_cover_art"], True)

    def test_console_handler(self):
        """Test ConsoleHandler logic"""
        handler = ConsoleHandler()

        # Mock tqdm
        with patch("src.cli.cli_main.tqdm") as mock_tqdm:
            # First update creates tqdm
            handler.on_progress_updated(5, 10)
            mock_tqdm.assert_called_once()
            progress_bar_instance = mock_tqdm.return_value

            # Update again
            handler.on_progress_updated(6, 10)
            self.assertEqual(handler.progress_bar.n, 6)

            # Finish
            handler.on_progress_updated(10, 10)
            progress_bar_instance.close.assert_called()
            self.assertIsNone(handler.progress_bar)


if __name__ == "__main__":
    unittest.main()
