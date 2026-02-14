"""
Auralis - Utils Test Module
"""

import unittest
from pathlib import Path

from src.utils.file_utils import (
    sanitize_filename,
    format_filename,
    ensure_unique_filename
)


class TestFileUtils(unittest.TestCase):
    """Test file utility functions"""

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test with invalid characters
        # Special characters are removed, spaces replaced by underscores
        self.assertEqual(sanitize_filename("test<>:\"/\\|?*"), "test")

        # Test with leading/trailing spaces
        self.assertEqual(sanitize_filename(" test "), "test")

        # Test with normal filename (without extension)
        # Spaces become underscores
        self.assertEqual(sanitize_filename("normal file"), "normal_file")

        # Test that dots are removed (sanitizer is for name parts, not full filename with extension)
        self.assertEqual(sanitize_filename("normal_file.mp3"), "normal_filemp3")

    def test_format_filename(self):
        """Test filename formatting"""
        # Test with all parameters
        # Spaces become underscores, hyphen separates title and artist
        self.assertEqual(
            format_filename(title="Song Title", artist="Artist Name", extension=".mp3"),
            "Song_Title-Artist_Name.mp3"
        )

        # Test with missing artist
        self.assertEqual(
            format_filename(title="Song Title", artist=None, extension=".mp3"),
            "Song_Title.mp3"
        )

        # Test with movie instead of artist
        self.assertEqual(
            format_filename(title="Song Title", artist=None, movie="Movie Name", extension=".mp3"),
            "Song_Title-Movie_Name.mp3"
        )

    def test_ensure_unique_filename(self):
        """Test ensuring unique filenames"""
        # Create a temporary test file
        test_dir = Path("tests/temp")
        test_dir.mkdir(exist_ok=True)

        test_file = test_dir / "test.txt"
        with open(test_file, "w") as f:
            f.write("test")

        # Test with existing file
        unique_name = ensure_unique_filename(str(test_file))
        self.assertNotEqual(unique_name, str(test_file))
        # Expect "test (1).txt"
        self.assertTrue("(1).txt" in unique_name)

        # Clean up
        test_file.unlink()
        test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
