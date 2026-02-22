"""
Unit tests for the Bio Service module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.services.bio_service import BioService, LastFmBioProvider, WikipediaBioProvider


class TestWikipediaBioProvider(unittest.TestCase):
    """Tests for WikipediaBioProvider."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = WikipediaBioProvider()

    @patch("src.services.bio_service.BeautifulSoup")
    @patch("src.services.bio_service.requests.get")
    def test_get_bio_success(self, mock_get, mock_bs):
        """Test successful bio retrieval."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Content doesn't matter much if we mock BS, but keeping it for completeness
        mock_response.content = b"<html>...</html>"
        mock_get.return_value = mock_response

        # Mock BeautifulSoup behavior
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        # Determine logic path in WikipediaBioProvider.get_bio
        # It finds div id="mw-content-text"
        # Then finds all 'p'
        # Iterates p, extracts text

        mock_content_div = MagicMock()
        mock_soup.find.return_value = mock_content_div

        # Paragraphs
        p1 = MagicMock()
        p1.get_text.return_value = ""  # First empty

        p2 = MagicMock()
        p2_text = (
            "The Beatles were an English rock band formed in Liverpool in 1960. With a line-up comprising John Lennon, "
            "Paul McCartney, George Harrison and Ringo Starr, they are regarded as the most influential band of all time.[1]"
        )
        p2.get_text.return_value = p2_text

        mock_content_div.find_all.return_value = [p1, p2]

        bio = self.provider.get_bio("The Beatles")

        self.assertIsNotNone(bio)
        self.assertIn("were an English rock band", bio)
        self.assertNotIn("[1]", bio)  # citation removed
        self.assertTrue(mock_get.called)

    @patch("src.services.bio_service.requests.get")
    def test_get_bio_not_found(self, mock_get):
        """Test bio not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        bio = self.provider.get_bio("Unknown Artist 12345")

        self.assertIsNone(bio)
        # Should try base URL + suffixes
        self.assertGreaterEqual(mock_get.call_count, 1)

    @patch("src.services.bio_service.BeautifulSoup")
    @patch("src.services.bio_service.requests.get")
    def test_get_bio_disambiguation(self, mock_get, mock_bs):
        """Test retrieval with disambiguation suffix."""
        # First call fails (404), second call succeeds (200)
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 404

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.content = b"<html>...</html>"

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        # Mock BS for the successful call
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        mock_content_div = MagicMock()
        mock_soup.find.return_value = mock_content_div

        p = MagicMock()
        p.get_text.return_value = (
            "A band bio that is long enough to pass the length check of 50 characters. This ensures the test passes."
        )

        mock_content_div.find_all.return_value = [p]

        bio = self.provider.get_bio("Common Name")

        self.assertEqual(
            bio,
            "A band bio that is long enough to pass the length check of 50 characters. This ensures the test passes.",
        )
        self.assertEqual(mock_get.call_count, 2)


class TestLastFmBioProvider(unittest.TestCase):
    """Tests for LastFmBioProvider."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset environment
        self.env_patcher = patch.dict(
            os.environ, {"LASTFM_API_KEY": "test_key", "LASTFM_API_SECRET": "test_secret"}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()

    @patch("src.services.bio_service.pylast")
    @patch("src.services.bio_service.HAS_LASTFM", True)
    def test_init_success(self, mock_pylast):
        """Test successful initialization."""
        provider = LastFmBioProvider()
        self.assertTrue(provider.available)
        self.assertIsNotNone(provider.network)

    @patch("src.services.bio_service.HAS_LASTFM", False)
    def test_init_no_library(self):
        """Test initialization when pylast is missing."""
        provider = LastFmBioProvider()
        self.assertFalse(provider.available)
        self.assertIsNone(provider.network)

    @patch("src.services.bio_service.BeautifulSoup")
    @patch("src.services.bio_service.pylast")
    @patch("src.services.bio_service.HAS_LASTFM", True)
    def test_get_bio_success(self, mock_pylast, mock_bs):
        """Test successful bio retrieval."""
        provider = LastFmBioProvider()

        # Mock network and artist
        mock_network = MagicMock()
        mock_artist = MagicMock()
        mock_artist.get_bio_summary.return_value = (
            "Test bio. <a href='...'>Read more on Last.fm</a>"
        )

        provider.network = mock_network
        mock_network.get_artist.return_value = mock_artist

        # Mock BeautifulSoup used in clean_html
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        mock_soup.get_text.return_value = "Test bio."

        bio = provider.get_bio("Artist")

        self.assertEqual(bio, "Test bio.")
        mock_network.get_artist.assert_called_with("Artist")

    @patch("src.services.bio_service.pylast")
    @patch("src.services.bio_service.HAS_LASTFM", True)
    def test_get_bio_not_found(self, mock_pylast):
        """Test bio not found/error."""
        provider = LastFmBioProvider()

        mock_network = MagicMock()
        provider.network = mock_network
        mock_network.get_artist.side_effect = Exception("Artist not found")

        bio = provider.get_bio("Unknown")

        self.assertIsNone(bio)


class TestBioService(unittest.TestCase):
    """Tests for BioService."""

    @patch("src.services.bio_service.WikipediaBioProvider")
    @patch("src.services.bio_service.LastFmBioProvider")
    def test_get_artist_bio_priority(self, MockLastFm, MockWiki):
        """Test provider priority."""
        # Setup mocks
        mock_lastfm = MockLastFm.return_value
        mock_lastfm.available = True
        mock_lastfm.name = "Last.fm"
        mock_lastfm.get_bio.return_value = "Last.fm Bio"

        mock_wiki = MockWiki.return_value
        mock_wiki.name = "Wikipedia"
        mock_wiki.get_bio.return_value = "Wiki Bio"

        service = BioService()

        # Verify order: Last.fm first
        bio = service.get_artist_bio("Artist")
        self.assertEqual(bio, "Last.fm Bio")
        mock_lastfm.get_bio.assert_called_once()
        mock_wiki.get_bio.assert_not_called()

    @patch("src.services.bio_service.WikipediaBioProvider")
    @patch("src.services.bio_service.LastFmBioProvider")
    def test_get_artist_bio_fallback(self, MockLastFm, MockWiki):
        """Test fallback to next provider."""
        # Setup mocks
        mock_lastfm = MockLastFm.return_value
        mock_lastfm.available = True
        mock_lastfm.get_bio.return_value = None

        mock_wiki = MockWiki.return_value
        mock_wiki.get_bio.return_value = "Wiki Bio"

        service = BioService()

        bio = service.get_artist_bio("Artist")
        self.assertEqual(bio, "Wiki Bio")
        mock_lastfm.get_bio.assert_called_once()
        mock_wiki.get_bio.assert_called_once()

    @patch("src.services.bio_service.WikipediaBioProvider")
    @patch("src.services.bio_service.LastFmBioProvider")
    def test_get_artist_bio_none_found(self, MockLastFm, MockWiki):
        """Test when no bio is found."""
        mock_lastfm = MockLastFm.return_value
        mock_lastfm.available = True
        mock_lastfm.get_bio.return_value = None

        mock_wiki = MockWiki.return_value
        mock_wiki.get_bio.return_value = None

        service = BioService()

        bio = service.get_artist_bio("Artist")
        self.assertIsNone(bio)
