"""
Unit tests for MetadataSanitizer
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


class MockMP3(MagicMock):
    pass


class MockID3(MagicMock):
    pass


class MockFLAC(MagicMock):
    pass


class TestMetadataSanitizer(unittest.TestCase):
    """Test cases for MetadataSanitizer"""

    def setUp(self) -> None:
        # Patch sys.modules to inject our mocks
        self.modules_patcher = patch.dict(sys.modules)
        self.modules_patcher.start()

        # Create mock mutagen modules
        mock_mutagen = MagicMock()

        mock_id3_module = MagicMock()
        mock_id3_module.ID3 = MockID3
        mock_id3_module.ID3NoHeaderError = Exception

        mock_mp3_module = MagicMock()
        mock_mp3_module.MP3 = MockMP3

        mock_flac_module = MagicMock()
        mock_flac_module.FLAC = MockFLAC

        sys.modules["mutagen"] = mock_mutagen
        sys.modules["mutagen.id3"] = mock_id3_module
        sys.modules["mutagen.mp3"] = mock_mp3_module
        sys.modules["mutagen.flac"] = mock_flac_module

        # Reload the module under test
        if "src.services.metadata_sanitizer" in sys.modules:
            del sys.modules["src.services.metadata_sanitizer"]

        import src.services.metadata_sanitizer

        self.module = src.services.metadata_sanitizer
        self.sanitizer = self.module.MetadataSanitizer()

    def tearDown(self) -> None:
        self.modules_patcher.stop()

    @patch("src.services.metadata_sanitizer.mutagen.File")
    def test_sanitize_mp3_remove_id3v1(self, mock_file):
        """Test removing ID3v1 tags from MP3"""
        mock_audio_file = MagicMock()
        mock_file.return_value = mock_audio_file

        # Run test
        result = self.sanitizer.sanitize(
            "test.mp3", {"remove_id3v1": True, "remove_comments": False, "trim_whitespace": False}
        )

        self.assertFalse(result)

    @patch("src.services.metadata_sanitizer.mutagen.File")
    def test_remove_comments_id3(self, mock_file):
        """Test removing comments from ID3 tags"""
        # Setup mock with ID3 tags including comments
        mock_audio = MagicMock()

        # Create a mock that satisfies isinstance(..., ID3)
        mock_tags = MockID3()
        mock_audio.tags = mock_tags

        # Mock keys() to return list
        mock_tags.keys.return_value = ["COMM:desc:eng", "TIT2"]

        mock_file.return_value = mock_audio

        result = self.sanitizer.sanitize(
            "test.mp3", {"remove_comments": True, "trim_whitespace": False}
        )

        mock_audio.tags.__delitem__.assert_called_with("COMM:desc:eng")
        self.assertTrue(result)
        mock_audio.save.assert_called()

    @patch("src.services.metadata_sanitizer.mutagen.File")
    def test_trim_whitespace_flac(self, mock_file):
        """Test trimming whitespace from FLAC tags"""
        # Setup mock FLAC
        mock_audio = MockFLAC()
        # Add keys method
        mock_audio.keys.return_value = ["artist", "title"]
        # Ensure hasattr(audio, "comments") is True
        mock_audio.comments = {}
        # Ensure tags attribute does not exist or is not ID3
        del mock_audio.tags

        def getitem(key):
            if key == "artist":
                return ["  Artist  "]
            if key == "title":
                return ["Title"]
            return []

        mock_audio.__getitem__.side_effect = getitem

        mock_file.return_value = mock_audio

        result = self.sanitizer.sanitize(
            "test.flac", {"trim_whitespace": True, "remove_comments": False}
        )

        mock_audio.__setitem__.assert_called_with("artist", ["Artist"])
        self.assertTrue(result)

    @patch("src.services.metadata_sanitizer.mutagen.File")
    def test_remove_padding_mp3(self, mock_file):
        """Test removing padding from MP3"""
        mock_audio = MockMP3()  # Mock MP3
        mock_audio.tags = MagicMock()
        # Ensure mock_audio.tags evaluates to True
        mock_audio.tags.__bool__.return_value = True

        mock_file.return_value = mock_audio

        result = self.sanitizer.sanitize(
            "test.mp3", {"remove_padding": True, "trim_whitespace": False, "remove_comments": False}
        )

        mock_audio.tags.save.assert_called_with("test.mp3", padding=0)
        self.assertTrue(result)
