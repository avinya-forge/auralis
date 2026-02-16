"""
Auralis - Audio Utilities Test Module
"""

import unittest
from unittest.mock import MagicMock, patch

from src.utils.audio_utils import (
    get_audio_fingerprint,
    get_audio_metadata,
    is_audio_file,
    set_album_art,
    set_audio_metadata,
)


class TestAudioUtils(unittest.TestCase):
    """Test audio utility functions"""

    def setUp(self):
        """Set up test environment"""
        self.mock_file_path = "/path/to/test.mp3"
        self.mock_flac_path = "/path/to/test.flac"

    def test_get_audio_metadata_mp3(self):
        """Test getting metadata from MP3 file"""
        with patch("src.utils.audio_utils.mutagen") as mock_mutagen:
            mock_mp3 = MagicMock()
            mock_mutagen.File.return_value = mock_mp3

            # Setup mock MP3 class
            class MockMP3:
                pass

            mock_mutagen.mp3.MP3 = MockMP3
            mock_mp3.__class__ = MockMP3

            # Configure mock_mp3 behavior
            mock_mp3.__contains__.side_effect = lambda key: key in {
                "TPE1",
                "TIT2",
                "TALB",
                "TDRC",
                "TCON",
                "TRCK",
            }
            mock_mp3.__getitem__.side_effect = lambda key: {
                "TPE1": ["Artist"],
                "TIT2": ["Title"],
                "TALB": ["Album"],
                "TDRC": ["2023"],
                "TCON": ["Genre"],
                "TRCK": ["1"],
            }.get(key)

            # Mock info
            mock_mp3.info.bitrate = 320000
            mock_mp3.info.length = 180
            mock_mp3.info.sample_rate = 44100

            metadata = get_audio_metadata(self.mock_file_path)

            self.assertEqual(metadata["artist"], "['Artist']")
            self.assertEqual(metadata["title"], "['Title']")
            self.assertEqual(metadata["album"], "['Album']")
            self.assertEqual(metadata["year"], "['2023']")
            self.assertEqual(metadata["genre"], "['Genre']")
            self.assertEqual(metadata["track"], "['1']")
            self.assertEqual(metadata["bitrate"], 320000)
            self.assertEqual(metadata["length"], 180)
            self.assertEqual(metadata["sample_rate"], 44100)

    def test_get_audio_metadata_flac(self):
        """Test getting metadata from FLAC file"""
        with patch("src.utils.audio_utils.mutagen") as mock_mutagen:
            mock_flac = MagicMock()
            mock_mutagen.File.return_value = mock_flac

            # Setup mock FLAC class
            class MockFLAC:
                pass

            mock_mutagen.flac.FLAC = MockFLAC
            mock_flac.__class__ = MockFLAC

            # Also setup MP3 class to be a valid type for isinstance check
            class MockMP3:
                pass

            mock_mutagen.mp3.MP3 = MockMP3

            # Configure mock_flac behavior
            mock_flac.__contains__.side_effect = lambda key: key in {
                "artist",
                "title",
                "album",
                "date",
                "genre",
                "tracknumber",
            }
            mock_flac.__getitem__.side_effect = lambda key: {
                "artist": ["Artist"],
                "title": ["Title"],
                "album": ["Album"],
                "date": ["2023"],
                "genre": ["Genre"],
                "tracknumber": ["1"],
            }.get(key)

            # Mock info
            mock_flac.info.bits_per_sample = 16
            mock_flac.info.sample_rate = 44100
            mock_flac.info.length = 180

            metadata = get_audio_metadata(self.mock_flac_path)

            self.assertEqual(metadata["artist"], "Artist")
            self.assertEqual(metadata["title"], "Title")
            self.assertEqual(metadata["album"], "Album")
            self.assertEqual(metadata["year"], "2023")
            self.assertEqual(metadata["genre"], "Genre")
            self.assertEqual(metadata["track"], "1")
            self.assertEqual(metadata["bitrate"], 16 * 44100)

    def test_set_audio_metadata_mp3(self):
        """Test setting metadata for MP3 file"""
        metadata = {
            "artist": "New Artist",
            "title": "New Title",
            "album": "New Album",
            "year": "2024",
            "genre": "New Genre",
            "track": "2",
        }

        with patch("src.utils.audio_utils.mutagen") as mock_mutagen:
            mock_mp3 = MagicMock()
            mock_mutagen.File.return_value = mock_mp3

            # Setup mock MP3 class
            class MockMP3:
                def save(self):
                    pass

                def __setitem__(self, k, v):
                    pass

            mock_mutagen.mp3.MP3 = MockMP3
            mock_mp3.__class__ = MockMP3

            result = set_audio_metadata(self.mock_file_path, metadata)

            self.assertTrue(result)
            mock_mp3.save.assert_called_once()
            # Check if tags were set (simplified check)
            self.assertTrue(mock_mp3.__setitem__.called)

    @patch("src.utils.audio_utils.acoustid.fingerprint_file")
    def test_get_audio_fingerprint(self, mock_fingerprint):
        """Test getting audio fingerprint"""
        mock_fingerprint.return_value = (180, "fingerprint_hash")

        duration, fingerprint = get_audio_fingerprint(self.mock_file_path)

        self.assertEqual(duration, 180)
        self.assertEqual(fingerprint, "fingerprint_hash")

    @patch("src.utils.audio_utils.acoustid.fingerprint_file")
    def test_get_audio_fingerprint_error(self, mock_fingerprint):
        """Test getting audio fingerprint with error"""
        mock_fingerprint.side_effect = Exception("Error")

        duration, fingerprint = get_audio_fingerprint(self.mock_file_path)

        self.assertIsNone(duration)
        self.assertIsNone(fingerprint)

    @patch("src.utils.audio_utils.requests.get")
    @patch("src.utils.audio_utils.ID3")
    def test_set_album_art_mp3_url(self, mock_id3, mock_get):
        """Test setting album art for MP3 from URL"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"image_data"
        mock_get.return_value = mock_response

        mock_audio = MagicMock()
        mock_id3.return_value = mock_audio

        result = set_album_art(self.mock_file_path, image_url="http://example.com/image.jpg")

        self.assertTrue(result)
        mock_audio.add.assert_called()
        mock_audio.save.assert_called()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_is_audio_file(self, mock_mutagen_file):
        """Test checking if file is audio file"""
        # Test valid extension and valid file
        mock_mutagen_file.return_value = MagicMock()
        self.assertTrue(is_audio_file("song.mp3"))

        # Test invalid extension
        self.assertFalse(is_audio_file("image.jpg"))

        # Test valid extension but invalid file (mutagen fails)
        mock_mutagen_file.return_value = None
        self.assertFalse(is_audio_file("broken.mp3"))

        # Test exception
        mock_mutagen_file.side_effect = Exception("Error")
        self.assertFalse(is_audio_file("error.mp3"))


if __name__ == "__main__":
    unittest.main()
