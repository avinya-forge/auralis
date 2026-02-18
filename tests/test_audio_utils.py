"""
Unit tests for audio_utils.py
"""

import unittest
from unittest.mock import MagicMock, patch

# Dependencies are mocked in conftest.py if missing
import acoustid
import mutagen
import requests
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import APIC

from src.utils.audio_utils import (
    AudioMetadataHandler,
    get_album_art,
    get_audio_metadata,
    set_album_art,
    set_audio_metadata,
)


class TestAudioMetadataHandler(unittest.TestCase):
    def setUp(self):
        self.mp3_path = "test.mp3"
        self.flac_path = "test.flac"

    @patch("src.utils.audio_utils.mutagen.File")
    def test_load_mp3(self, mock_mutagen_file):
        # Setup mock
        mock_audio = MP3()
        mock_mutagen_file.return_value = mock_audio

        # Test
        handler = AudioMetadataHandler(self.mp3_path)

        # Verify
        self.assertTrue(handler.is_valid())
        mock_mutagen_file.assert_called_once_with(self.mp3_path)

    @patch("src.utils.audio_utils.mutagen.File")
    def test_load_flac(self, mock_mutagen_file):
        # Setup mock
        mock_audio = FLAC()
        mock_mutagen_file.return_value = mock_audio

        # Test
        handler = AudioMetadataHandler(self.flac_path)

        # Verify
        self.assertTrue(handler.is_valid())

    @patch("src.utils.audio_utils.mutagen.File")
    def test_load_failed(self, mock_mutagen_file):
        # Setup mock
        mock_mutagen_file.side_effect = Exception("Load error")

        # Test
        handler = AudioMetadataHandler("invalid.mp3")

        # Verify
        self.assertFalse(handler.is_valid())

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_mp3(self, mock_mutagen_file):
        # Setup mock
        mock_audio = MP3()
        mock_audio.__contains__.side_effect = lambda key: key in ["TPE1", "TIT2"]
        mock_audio.__getitem__.side_effect = lambda key: {"TPE1": "Artist", "TIT2": "Title"}[key]
        mock_audio.info.bitrate = 128000
        mock_audio.info.length = 180
        mock_audio.info.sample_rate = 44100
        mock_mutagen_file.return_value = mock_audio

        # Test
        metadata = get_audio_metadata(self.mp3_path)

        # Verify
        self.assertEqual(metadata["artist"], "Artist")
        self.assertEqual(metadata["title"], "Title")
        self.assertEqual(metadata["bitrate"], 128000)

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_flac(self, mock_mutagen_file):
        # Setup mock
        mock_audio = FLAC()
        mock_audio.__contains__.side_effect = lambda key: key in ["artist", "title"]
        mock_audio.__getitem__.side_effect = lambda key: {"artist": ["Artist"], "title": ["Title"]}[
            key
        ]
        mock_audio.info.bits_per_sample = 16
        mock_audio.info.sample_rate = 44100
        mock_audio.info.length = 180
        # Ensure bitrate is not present so it falls back to calculation
        del mock_audio.info.bitrate
        mock_mutagen_file.return_value = mock_audio

        # Test
        metadata = get_audio_metadata(self.flac_path)

        # Verify
        self.assertEqual(metadata["artist"], "Artist")
        self.assertEqual(metadata["title"], "Title")
        self.assertEqual(metadata["bitrate"], 16 * 44100)

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_mp3(self, mock_mutagen_file):
        # Setup mock
        mock_audio = MP3()
        mock_mutagen_file.return_value = mock_audio

        metadata = {"artist": "New Artist", "title": "New Title"}

        # Test
        result = set_audio_metadata(self.mp3_path, metadata)

        # Verify
        self.assertTrue(result)
        mock_audio.save.assert_called_once()
        # Check if tags were set (simplified check as we use MP3_TAG_CLASSES)
        self.assertTrue(mock_audio.__setitem__.called)

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_flac(self, mock_mutagen_file):
        # Setup mock
        mock_audio = FLAC()
        mock_mutagen_file.return_value = mock_audio

        metadata = {"artist": "New Artist", "title": "New Title"}

        # Test
        result = set_audio_metadata(self.flac_path, metadata)

        # Verify
        self.assertTrue(result)
        mock_audio.save.assert_called_once()
        mock_audio.__setitem__.assert_any_call("artist", "New Artist")
        mock_audio.__setitem__.assert_any_call("title", "New Title")

    @patch("requests.get")
    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_album_art_url(self, mock_mutagen_file, mock_requests_get):
        # Setup mock
        mock_audio = MP3()
        mock_audio.tags = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_data"
        mock_requests_get.return_value = mock_response

        # Test
        result = set_album_art(self.mp3_path, image_url="http://example.com/cover.jpg")

        # Verify
        self.assertTrue(result)
        mock_audio.save.assert_called_once()
        mock_audio.tags.add.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_mp3(self, mock_mutagen_file):
        # Setup mock
        mock_audio = MP3()
        mock_tag = MagicMock()
        mock_tag.FrameID = "APIC"
        mock_tag.data = b"fake_image_data"
        mock_audio.tags.values.return_value = [mock_tag]
        mock_mutagen_file.return_value = mock_audio

        # Test
        data = get_album_art(self.mp3_path)

        # Verify
        self.assertEqual(data, b"fake_image_data")


if __name__ == "__main__":
    unittest.main()
