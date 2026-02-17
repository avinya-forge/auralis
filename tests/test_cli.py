"""
Unit tests for the CLI module
"""

import argparse
import sys
import unittest
from unittest.mock import MagicMock, patch


def mock_module_if_missing(module_name):
    """Mock a module if it cannot be imported"""
    try:
        __import__(module_name)
    except ImportError:
        sys.modules[module_name] = MagicMock()


# Mock dependencies if they are not installed (e.g. in minimal test environments)
mock_module_if_missing("PyQt6")
mock_module_if_missing("PyQt6.QtCore")
mock_module_if_missing("PyQt6.QtWidgets")
mock_module_if_missing("PyQt6.QtGui")
mock_module_if_missing("numpy")
mock_module_if_missing("librosa")
mock_module_if_missing("sklearn")
mock_module_if_missing("sklearn.metrics")
mock_module_if_missing("sklearn.metrics.pairwise")
mock_module_if_missing("soundfile")
mock_module_if_missing("pydub")
mock_module_if_missing("mutagen")
mock_module_if_missing("mutagen.mp3")
mock_module_if_missing("mutagen.flac")
mock_module_if_missing("mutagen.id3")
mock_module_if_missing("requests")
mock_module_if_missing("musicbrainzngs")
mock_module_if_missing("discogs_client")
mock_module_if_missing("acoustid")

# Import after potential mocking
from src.cli.cli_main import (  # noqa: E402
    run_metadata,
    run_organize,
    run_scan,
    setup_parser,
)


class TestCLI(unittest.TestCase):
    """Test cases for CLI module"""

    def setUp(self):
        self.parser = setup_parser()

    def test_setup_parser(self):
        """Test parser configuration"""
        args = self.parser.parse_args(["scan", "/tmp"])
        self.assertEqual(args.command, "scan")
        self.assertEqual(args.directories, ["/tmp"])

        args = self.parser.parse_args(["organize", "src", "dest"])
        self.assertEqual(args.command, "organize")
        self.assertEqual(args.source, "src")
        self.assertEqual(args.destination, "dest")

        args = self.parser.parse_args(["metadata", "src"])
        self.assertEqual(args.command, "metadata")
        self.assertEqual(args.source, "src")

    @patch("src.cli.cli_main.MusicScanner")
    def test_run_scan(self, mock_scanner_cls):
        """Test run_scan function"""
        mock_scanner = mock_scanner_cls.return_value
        mock_scanner.scan_directories.return_value = [{"path": "test.mp3"}]

        args = argparse.Namespace(directories=["/tmp"], extensions="mp3,flac", output_json=None)

        run_scan(args)

        mock_scanner.scan_directories.assert_called_with(
            ["/tmp"], {"file_extensions": ["mp3", "flac"]}
        )

    @patch("src.cli.cli_main.MusicOrganizer")
    @patch("src.cli.cli_main._load_files")
    def test_run_organize(self, mock_load_files, mock_organizer_cls):
        """Test run_organize function"""
        mock_load_files.return_value = [{"path": "test.mp3"}]
        mock_organizer = mock_organizer_cls.return_value
        mock_organizer.organize_files.return_value = {
            "total_files": 1,
            "organized_files": 1,
        }

        args = argparse.Namespace(
            source="files.json",
            destination="/dest",
            dry_run=True,
            no_language=False,
            no_similarity=True,
        )

        run_organize(args)

        mock_load_files.assert_called_with("files.json")
        mock_organizer.organize_files.assert_called()

        # Check options
        call_args = mock_organizer.organize_files.call_args
        self.assertEqual(call_args[0][1], "/dest")
        self.assertTrue(call_args[0][2]["organize_by_language"])
        self.assertFalse(call_args[0][2]["detect_audio_similarity"])

    @patch("src.cli.cli_main.MetadataService")
    @patch("src.cli.cli_main._load_files")
    def test_run_metadata(self, mock_load_files, mock_service_cls):
        """Test run_metadata function"""
        mock_load_files.return_value = [{"path": "test.mp3"}]
        mock_service = mock_service_cls.return_value
        mock_service.update_metadata.return_value = [{"path": "test.mp3"}]

        args = argparse.Namespace(source="files.json", musicbrainz=True, discogs=False, lyrics=True)

        run_metadata(args)

        mock_load_files.assert_called_with("files.json")
        mock_service.update_metadata.assert_called()

        # Check options
        call_args = mock_service.update_metadata.call_args
        self.assertTrue(call_args[0][1]["use_musicbrainz"])
        self.assertFalse(call_args[0][1]["use_discogs"])
        self.assertTrue(call_args[0][1]["fetch_lyrics"])


if __name__ == "__main__":
    unittest.main()
