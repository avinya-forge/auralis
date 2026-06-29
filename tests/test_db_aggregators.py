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

    def test_spotify_aggregator_enabled_stub(self):
        agg = SpotifyAggregator(client_id="id", client_secret="secret")
        self.assertTrue(agg.enabled)
        results = agg.search_track("a", "t")
        self.assertEqual(results[0]["source"], "spotify")

    @patch.object(MusicBrainzAggregator, "search_recording")
    def test_musicbrainz_batch_seed(self, mock_search):
        mock_search.return_value = [{"mbid": "1", "title": "T1"}]
        agg = MusicBrainzAggregator()
        queries = [{"artist": "A1", "title": "T1"}, {"artist": "A2", "title": "T2"}]
        results = agg.batch_seed(queries)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["results"][0]["title"], "T1")

    def test_spotify_batch_seed(self):
        agg = SpotifyAggregator(client_id="id", client_secret="secret")
        queries = [{"artist": "A1", "title": "T1"}, {"artist": "A2", "title": "T2"}]
        results = agg.batch_seed(queries)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["results"][0]["artist"], "A1")


if __name__ == "__main__":
    unittest.main()
