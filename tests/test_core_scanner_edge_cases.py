import unittest
from unittest.mock import patch

from PyQt6.QtCore import QCoreApplication
import asyncio

from src.core.scanner import MusicScanner

# Ensure QCoreApplication exists
app = QCoreApplication.instance() or QCoreApplication([])


class TestScannerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.scanner = MusicScanner()

    @patch("os.walk")
    def test_scan_permission_error(self, mock_walk):
        """Test scanning a directory that raises PermissionError"""
        mock_walk.side_effect = PermissionError("Access denied")

        # Should catch exception and print error (or log), returning empty list
        results = asyncio.run(self.scanner.scan_directories(["/root/protected"]))
        self.assertEqual(results, [])

    @patch("os.walk")
    def test_scan_os_error(self, mock_walk):
        """Test scanning a directory that raises OSError"""
        mock_walk.side_effect = OSError("Disk error")
        results = asyncio.run(self.scanner.scan_directories(["/broken/disk"]))
        self.assertEqual(results, [])

    @patch("mutagen.File")
    @patch("os.stat")
    @patch("hashlib.md5")
    def test_corrupt_file(self, mock_md5, mock_stat, mock_mutagen):
        """Test processing a corrupt audio file"""
        mock_stat.return_value.st_size = 1024
        mock_stat.return_value.st_mtime = 1234567890
        mock_md5.return_value.hexdigest.return_value = "hash"

        # Mutagen fails
        mock_mutagen.side_effect = Exception("Corrupt header")

        # Should still return basic file info
        file_info = asyncio.run(self.scanner._extract_file_info("/path/to/corrupt.mp3"))

        self.assertIsNotNone(file_info)
        self.assertEqual(file_info["filename"], "corrupt.mp3")
        # Metadata might be inferred from filename if possible, otherwise empty
        # corrupt.mp3 has no ' - ' so it should return None, None for parse_filename
        self.assertEqual(file_info.get("metadata"), {})

    def test_parse_filename_edge_cases(self):
        """Test filename parsing with edge cases"""
        # "Artist - " (missing title)
        a, t = self.scanner._parse_filename("MyArtist - .mp3")
        self.assertEqual(a, "MyArtist")
        self.assertEqual(t, "")

        # " - Title" (missing artist)
        a, t = self.scanner._parse_filename(" - MyTitle.mp3")
        self.assertEqual(a, "")
        self.assertEqual(t, "MyTitle")

        # "Artist_-_Title"
        a, t = self.scanner._parse_filename("Artist_-_Title.mp3")
        self.assertEqual(a, "Artist")
        self.assertEqual(t, "Title")

        # No pattern
        a, t = self.scanner._parse_filename("JustFilename.mp3")
        self.assertIsNone(a)
        self.assertIsNone(t)

    @patch("builtins.open")
    def test_hash_calculation_error(self, mock_open):
        """Test hash calculation when file is locked or unreadable"""
        mock_open.side_effect = PermissionError("Locked")
        hash_val = self.scanner._calculate_file_hash("/locked/file.mp3")
        self.assertIsNone(hash_val)

    @patch("os.stat")
    def test_extract_file_info_error(self, mock_stat):
        """Test _extract_file_info when a critical error occurs"""
        mock_stat.side_effect = Exception("Critical FS Error")
        file_info = asyncio.run(self.scanner._extract_file_info("/path/to/file.mp3"))
        self.assertIsNone(file_info)
