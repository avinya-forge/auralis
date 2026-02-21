"""
Unit tests for Lyrics Providers (Musixmatch)
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.lyrics_service import MusixmatchLyricsProvider


class TestMusixmatchLyricsProvider:
    @pytest.fixture
    def provider(self):
        session = MagicMock()
        return MusixmatchLyricsProvider(session)

    @patch("src.services.lyrics_service.BeautifulSoup")
    def test_get_lyrics_success(self, mock_bs, provider):
        """Test successful lyrics retrieval from Musixmatch"""
        # Mock soup for search
        mock_search_soup = MagicMock()
        mock_title_link = MagicMock()
        mock_title_link.get.return_value = "/lyrics/artist/song"
        mock_search_soup.find.return_value = mock_title_link

        # Mock soup for lyrics
        mock_lyrics_soup = MagicMock()
        mock_span1 = MagicMock()
        mock_span1.get_text.return_value = "Verse 1"
        mock_span2 = MagicMock()
        mock_span2.get_text.return_value = "Verse 2"
        mock_lyrics_soup.find_all.return_value = [mock_span1, mock_span2]

        # Setup side effect for BeautifulSoup constructor
        mock_bs.side_effect = [mock_search_soup, mock_lyrics_soup]

        # Mock responses
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.text = "search html"

        mock_lyrics_response = MagicMock()
        mock_lyrics_response.status_code = 200
        mock_lyrics_response.text = "lyrics html"

        provider.session.get.side_effect = [mock_search_response, mock_lyrics_response]

        lyrics = provider.get_lyrics("Test Artist", "Test Song")

        assert lyrics == "Verse 1\nVerse 2"

        # Verify calls
        assert provider.session.get.call_count == 2
        # Check URL encoding in first call
        args, _ = provider.session.get.call_args_list[0]
        assert "Test%20Artist%20Test%20Song" in args[0] or "Test+Artist+Test+Song" in args[0]

    def test_get_lyrics_not_found_search(self, provider):
        """Test lyrics not found (no search results)"""
        # Mock soup to return no link
        mock_bs_instance = MagicMock()
        mock_bs_instance.find.return_value = None

        with patch("src.services.lyrics_service.BeautifulSoup", return_value=mock_bs_instance):
            mock_response = MagicMock()
            mock_response.status_code = 200
            provider.session.get.return_value = mock_response

            lyrics = provider.get_lyrics("Artist", "Song")
            assert lyrics is None

    def test_get_lyrics_not_found_page(self, provider):
        """Test lyrics not found (page fetch error)"""
        # Mock search success
        mock_bs_instance = MagicMock()
        mock_link = MagicMock()
        mock_link.get.return_value = "/link"
        mock_bs_instance.find.return_value = mock_link

        with patch("src.services.lyrics_service.BeautifulSoup", return_value=mock_bs_instance):
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200

            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 404

            provider.session.get.side_effect = [mock_response_ok, mock_response_fail]

            lyrics = provider.get_lyrics("Artist", "Song")
            assert lyrics is None
