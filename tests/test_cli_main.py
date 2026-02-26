import argparse
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli.cli_main import run_cli, run_organize, run_scan, setup_parser  # noqa: E402


class TestCLIMain(unittest.TestCase):
    def test_setup_parser(self):
        parser = setup_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

        # Test scan command parsing
        args = parser.parse_args(["scan", "/tmp"])
        self.assertEqual(args.command, "scan")
        self.assertEqual(args.directories, ["/tmp"])

        # Test organize command parsing
        args = parser.parse_args(["organize", "/src", "/dst"])
        self.assertEqual(args.command, "organize")
        self.assertEqual(args.source, "/src")
        self.assertEqual(args.destination, "/dst")

    @patch("src.cli.cli_main.run_scan")
    @patch("src.cli.cli_main.setup_parser")
    def test_run_cli_scan(self, mock_setup_parser, mock_run_scan):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            command="scan", log_level="INFO", debug=False
        )
        mock_setup_parser.return_value = mock_parser

        # Mock QCoreApplication to avoid Qt init issues
        with patch("src.cli.cli_main.QCoreApplication"):
            with patch("logging.basicConfig"):
                # Mock HAS_PYQT to True to pass the check
                with patch("src.cli.cli_main.HAS_PYQT", True):
                    run_cli()
                    mock_run_scan.assert_called_once()

    @patch("src.core.scanner.MusicScanner")
    def test_run_scan(self, MockScanner):
        mock_scanner = MockScanner.return_value
        mock_scanner.scan_directories.return_value = [{"path": "/tmp/song.mp3"}]

        args = argparse.Namespace(
            directories=["/tmp"], extensions=None, exclude=None, depth=10, output_json=None
        )

        with patch("builtins.print"):
            run_scan(args)

        mock_scanner.scan_directories.assert_called_once()

    @patch("src.core.organizer.MusicOrganizer")
    @patch("src.cli.cli_main._load_files")
    def test_run_organize(self, mock_load_files, MockOrganizer):
        mock_files = [{"path": "/tmp/song.mp3"}]
        mock_load_files.return_value = mock_files

        mock_organizer = MockOrganizer.return_value
        mock_organizer.organize_files.return_value = {"total_files": 1, "organized_files": 1}

        args = argparse.Namespace(
            source="/tmp",
            destination="/out",
            dry_run=False,
            no_language=False,
            no_similarity=False,
            no_rename=False,
            keep_duplicates=False,
            keep_empty_dirs=False,
            template=None,
        )

        with patch("builtins.print"):
            run_organize(args)

        mock_organizer.organize_files.assert_called_once()


if __name__ == "__main__":
    unittest.main()
