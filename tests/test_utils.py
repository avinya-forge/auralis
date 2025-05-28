"""
Auralis - Utils Test Module
"""

import os
import unittest
from pathlib import Path

from src.utils.file_utils import (
    sanitize_filename,
    format_filename,
    ensure_unique_filename,
    get_file_hash
)

class TestFileUtils(unittest.TestCase):
    """Test file utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test with invalid characters
        self.assertEqual(sanitize_filename("test<>:\"/\\|?*"), "test_________")
        
        # Test with leading/trailing spaces
        self.assertEqual(sanitize_filename(" test "), "test")
        
        # Test with normal filename
        self.assertEqual(sanitize_filename("normal_file.mp3"), "normal_file.mp3")
    
    def test_format_filename(self):
        """Test filename formatting"""
        # Test with all parameters
        self.assertEqual(
            format_filename(title="Song Title", artist="Artist Name", extension=".mp3"),
            "Song Title - Artist Name.mp3"
        )
        
        # Test with missing artist
        self.assertEqual(
            format_filename(title="Song Title", artist=None, extension=".mp3"),
            "Song Title.mp3"
        )
        
        # Test with movie instead of artist
        self.assertEqual(
            format_filename(title="Song Title", artist=None, movie="Movie Name", extension=".mp3"),
            "Song Title - Movie Name.mp3"
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
        self.assertTrue("test (1).txt" in unique_name)
        
        # Clean up
        test_file.unlink()
        test_dir.rmdir()

if __name__ == "__main__":
    unittest.main() 