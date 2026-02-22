"""
Unit tests for GenreClassifier
"""

import unittest
from unittest.mock import MagicMock, patch

from mutagen.id3 import ID3NoHeaderError

from src.services.genre_service import GenreClassifier


class TestGenreClassifier(unittest.TestCase):
    """Test cases for GenreClassifier"""

    def setUp(self) -> None:
        self.classifier = GenreClassifier()

    @patch("src.services.genre_service.mutagen.File")
    def test_get_genre_success(self, mock_mutagen_file):
        """Test getting genre successfully"""
        # Mock successful return
        mock_audio = MagicMock()
        mock_audio.__contains__.side_effect = lambda key: key == "genre"
        mock_audio.__getitem__.side_effect = lambda key: ["Rock"] if key == "genre" else None
        mock_mutagen_file.return_value = mock_audio

        genre = self.classifier.get_genre("test.mp3")
        self.assertEqual(genre, "Rock")

    @patch("src.services.genre_service.mutagen.File")
    def test_get_genre_not_found(self, mock_mutagen_file):
        """Test getting genre when not present"""
        # Mock file found but no genre
        mock_audio = MagicMock()
        mock_audio.__contains__.return_value = False
        mock_mutagen_file.return_value = mock_audio

        genre = self.classifier.get_genre("test.mp3")
        self.assertIsNone(genre)

    @patch("src.services.genre_service.mutagen.File")
    def test_get_genre_error(self, mock_mutagen_file):
        """Test getting genre with error"""
        mock_mutagen_file.side_effect = Exception("Read error")

        genre = self.classifier.get_genre("test.mp3")
        self.assertIsNone(genre)

    @patch("src.services.genre_service.mutagen.File")
    def test_set_genre_success(self, mock_mutagen_file):
        """Test setting genre successfully"""
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        success = self.classifier.set_genre("test.mp3", "rock")
        self.assertTrue(success)
        mock_audio.__setitem__.assert_called_with("genre", "Rock")
        mock_audio.save.assert_called_once()

    @patch("src.services.genre_service.mutagen.File")
    def test_set_genre_empty(self, mock_mutagen_file):
        """Test setting empty genre"""
        success = self.classifier.set_genre("test.mp3", "")
        self.assertFalse(success)
        mock_mutagen_file.assert_not_called()

    @patch("src.services.genre_service.EasyID3")
    @patch("src.services.genre_service.mutagen.File")
    def test_set_genre_mp3_fallback(self, mock_mutagen_file, mock_easyid3):
        """Test fallback for MP3 when mutagen.File returns None"""
        mock_mutagen_file.return_value = None

        mock_audio = MagicMock()
        mock_easyid3.return_value = mock_audio

        # Test with .mp3 extension
        success = self.classifier.set_genre("test.mp3", "Jazz")

        self.assertTrue(success)
        mock_easyid3.assert_called_with("test.mp3")
        mock_audio.__setitem__.assert_called_with("genre", "Jazz")
        mock_audio.save.assert_called()

    @patch("src.services.genre_service.EasyID3")
    @patch("src.services.genre_service.mutagen.File")
    def test_set_genre_mp3_no_header_fallback(self, mock_mutagen_file, mock_easyid3):
        """Test fallback for MP3 when ID3 header is missing"""
        mock_mutagen_file.return_value = None

        # First EasyID3 call raises ID3NoHeaderError
        # Second call (constructor without args) returns new object
        mock_audio = MagicMock()
        mock_easyid3.side_effect = [ID3NoHeaderError("No header"), mock_audio]

        success = self.classifier.set_genre("test.mp3", "Pop")

        self.assertTrue(success)
        # Should call EasyID3() empty constructor
        # Note: side_effect consumes the calls
        self.assertEqual(mock_easyid3.call_count, 2)
        # Check that save was called with filename (initial save) and without (final save)
        mock_audio.save.assert_any_call("test.mp3")
        mock_audio.save.assert_called_with()

    @patch("src.services.genre_service.mutagen.File")
    def test_set_genre_unsupported_file(self, mock_mutagen_file):
        """Test setting genre on unsupported file type returning None"""
        mock_mutagen_file.return_value = None

        success = self.classifier.set_genre("test.txt", "Rock")
        self.assertFalse(success)

    def test_normalize_genre(self):
        """Test genre normalization"""
        self.assertEqual(self.classifier.normalize_genre("rock"), "Rock")
        self.assertEqual(self.classifier.normalize_genre("hip-hop"), "Hip-Hop")
        self.assertEqual(self.classifier.normalize_genre("  jazz  "), "Jazz")
        self.assertEqual(self.classifier.normalize_genre(""), "")
