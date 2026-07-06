import unittest
from unittest.mock import patch

from src.services.metadata.aggregators import MusicBrainzAggregator, SpotifyAggregator


class TestDBAggregators(unittest.TestCase):
    @patch("musicbrainzngs.search_recordings")
    def test_musicbrainz_search(self, mock_search):
        mock_search.return_value = {
            "recording-list": [
                {
                    "id": "mbid1",
                    "title": "Title 1",
                    "artist-credit-phrase": "Artist 1",
                    "ext:score": "100",
                }
            ]
        }

        agg = MusicBrainzAggregator()
        results = agg.search_recording("Artist 1", "Title 1")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["mbid"], "mbid1")
        self.assertEqual(results[0]["score"], 100)

    @patch("musicbrainzngs.get_recording_by_id")
    def test_musicbrainz_details(self, mock_get):
        mock_get.return_value = {
            "recording": {
                "title": "Full Title",
                "artist-credit-phrase": "Full Artist",
                "release-list": [{"title": "Album 1"}],
            }
        }

        agg = MusicBrainzAggregator()
        details = agg.get_details("mbid123")

        self.assertEqual(details["mbid"], "mbid123")
        self.assertEqual(details["title"], "Full Title")
        self.assertIn("Album 1", details["releases"])

    def test_spotify_aggregator_disabled(self):
        agg = SpotifyAggregator()
        self.assertFalse(agg.enabled)
        self.assertEqual(agg.search_track("a", "t"), [])

    @patch("spotipy.Spotify.search")
    @patch("spotipy.oauth2.SpotifyClientCredentials")
    def test_spotify_aggregator_enabled_search(self, mock_creds, mock_search):
        mock_search.return_value = {
            "tracks": {
                "items": [
                    {
                        "id": "spot1",
                        "name": "Title 1",
                        "artists": [{"name": "Artist 1"}],
                        "album": {"name": "Album 1"},
                        "popularity": 80,
                        "external_urls": {"spotify": "http://spotify.com"},
                    }
                ]
            }
        }

        with patch("src.services.metadata.aggregators.SPOTIPY_AVAILABLE", True):
            with patch("src.services.metadata.aggregators.SpotifyClientCredentials", mock_creds):
                agg = SpotifyAggregator(client_id="id", client_secret="secret")

        # Inject the mock search method onto the created client
        agg.client.search = mock_search

        results = agg.search_track("a", "t")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "spotify")
        self.assertEqual(results[0]["id"], "spot1")
        self.assertEqual(results[0]["title"], "Title 1")
        self.assertEqual(results[0]["artist"], "Artist 1")

    @patch.object(MusicBrainzAggregator, "search_recording")
    def test_musicbrainz_batch_seed(self, mock_search):
        mock_search.return_value = [{"mbid": "1", "title": "T1"}]
        agg = MusicBrainzAggregator()
        queries = [{"artist": "A1", "title": "T1"}, {"artist": "A2", "title": "T2"}]
        results = agg.batch_seed(queries)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["results"][0]["title"], "T1")

    @patch.object(SpotifyAggregator, "search_track")
    @patch("spotipy.oauth2.SpotifyClientCredentials")
    def test_spotify_batch_seed(self, mock_creds, mock_search):
        mock_search.return_value = [{"source": "spotify", "title": "T1"}]
        with patch("src.services.metadata.aggregators.SPOTIPY_AVAILABLE", True):
            with patch("src.services.metadata.aggregators.SpotifyClientCredentials", mock_creds):
                agg = SpotifyAggregator(client_id="id", client_secret="secret")

        queries = [{"artist": "A1", "title": "T1"}, {"artist": "A2", "title": "T2"}]
        results = agg.batch_seed(queries)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["results"][0]["title"], "T1")


if __name__ == "__main__":
    unittest.main()
