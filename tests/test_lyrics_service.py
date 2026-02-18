"""
Unit tests for Lyrics Service
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.lyrics_service import (
    GeniusProvider,
    LyricsService,
    TekstowoProvider,
)


class TestGeniusProvider:
    @pytest.fixture
    def provider(self):
        session = MagicMock()
        return GeniusProvider(session)

    @patch("src.services.lyrics_service.BeautifulSoup")
    def test_get_lyrics_success(self, mock_bs, provider):
        """Test successful lyrics retrieval from Genius"""
        # Mock BS
        mock_soup = mock_bs.return_value
        mock_soup  # silence unused variable warning if necessary, or just use it
        mock_div = MagicMock()
        mock_div.get_text.return_value = "Test Lyrics"
        mock_div.find_all.return_value = []  # no br tags
        mock_soup.find_all.return_value = [mock_div]

        # Mock search response
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "response": {
                "sections": [
                    {
                        "type": "song",
                        "hits": [
                            {
                                "result": {
                                    "primary_artist": {"name": "Test Artist"},
                                    "path": "/lyrics/test-song",
                                }
                            }
                        ],
                    }
                ]
            }
        }

        # Mock lyrics page response
        mock_lyrics_response = MagicMock()
        mock_lyrics_response.status_code = 200
        mock_lyrics_response.text = (
            '<html><div data-lyrics-container="true">Test Lyrics</div></html>'
        )

        provider.session.get.side_effect = [mock_search_response, mock_lyrics_response]

        # Call method
        lyrics = provider.get_lyrics("Test Artist", "Test Song")

        assert lyrics == "Test Lyrics"
        assert provider.session.get.call_count == 2

    def test_get_lyrics_not_found(self, provider):
        """Test lyrics not found on Genius"""
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {"response": {"sections": []}}

        provider.session.get.return_value = mock_search_response

        lyrics = provider.get_lyrics("Unknown", "Song")
        assert lyrics is None


class TestTekstowoProvider:
    @pytest.fixture
    def provider(self):
        session = MagicMock()
        return TekstowoProvider(session)

    @patch("src.services.lyrics_service.BeautifulSoup")
    def test_get_lyrics_success(self, mock_bs, provider):
        """Test successful lyrics retrieval from Tekstowo"""
        # Mock BS
        mock_soup = mock_bs.return_value
        mock_soup  # silence unused variable warning

        # For search page: find_all("a", class_="title")
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Test Artist - Test Song"
        mock_link.get.return_value = "/piosenka,artist,title.html"  # href

        # For lyrics page: find("div", class_="song-text")
        mock_lyrics_div = MagicMock()
        mock_lyrics_div.get_text.return_value = "Test Lyrics"
        mock_lyrics_div.find_all.return_value = []  # script tags etc

        # We need to distinguish between search page parsing and lyrics page parsing
        # But they use the same mock_bs instance usually if called in sequence?
        # No, BeautifulSoup is instantiated anew each time.
        # So mock_bs() returns a new mock each time?
        # Yes, return_value is the instance.
        # But here mock_bs is the CLASS.
        # If we use side_effect on the class instantiation...

        soup1 = MagicMock()
        soup1.find_all.return_value = [mock_link]  # Search results

        soup2 = MagicMock()
        soup2.find.return_value = mock_lyrics_div  # Lyrics div

        mock_bs.side_effect = [soup1, soup2]

        # Mock search response
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.text = "search html"

        # Mock lyrics page response
        mock_lyrics_response = MagicMock()
        mock_lyrics_response.status_code = 200
        mock_lyrics_response.text = "lyrics html"

        provider.session.get.side_effect = [mock_search_response, mock_lyrics_response]

        lyrics = provider.get_lyrics("Test Artist", "Test Song")
        assert lyrics == "Test Lyrics"

    def test_get_lyrics_not_found(self, provider):
        """Test lyrics not found on Tekstowo"""
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.text = "<html>No results</html>"

        provider.session.get.return_value = mock_search_response

        lyrics = provider.get_lyrics("Unknown", "Song")
        assert lyrics is None


class TestLyricsService:
    @pytest.fixture
    def service(self):
        with patch("src.services.lyrics_service.requests.Session"):
            service = LyricsService()
            # Clear providers to test registration logic or mock them
            service.providers = []
            return service

    def test_fetch_lyrics_fallback(self, service):
        """Test fallback to second provider if first fails"""
        provider1 = MagicMock()
        provider1.name = "Provider1"
        provider1.get_lyrics.return_value = None

        provider2 = MagicMock()
        provider2.name = "Provider2"
        provider2.get_lyrics.return_value = "Found Lyrics"

        service.register_provider(provider1)
        service.register_provider(provider2)

        lyrics = service.fetch_lyrics("Artist", "Title")

        assert lyrics == "Found Lyrics"
        provider1.get_lyrics.assert_called_once()
        provider2.get_lyrics.assert_called_once()

    def test_fetch_lyrics_cache(self, service):
        """Test caching of lyrics"""
        service.cache["artist|title"] = "Cached Lyrics"

        provider = MagicMock()
        service.register_provider(provider)

        lyrics = service.fetch_lyrics("Artist", "Title")

        assert lyrics == "Cached Lyrics"
        provider.get_lyrics.assert_not_called()
