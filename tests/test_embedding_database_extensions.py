import os
import tempfile
import unittest

import numpy as np

from src.modules.neu.embedding_database import EmbeddingDatabase


class TestEmbeddingDatabaseExtensions(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = EmbeddingDatabase(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_link_knowledge_graph(self):
        self.db.upsert_embedding("track_1", np.array([0.1, 0.2, 0.3]), "v1")
        self.db.link_knowledge_graph(
            "track_1", mbid="mbid-123", spotify_id="spotify-456", wikipedia_url="http://wiki/track"
        )

        links = self.db.get_knowledge_graph_links("track_1")
        self.assertIsNotNone(links)
        self.assertEqual(links[0], "mbid-123")
        self.assertEqual(links[1], "spotify-456")
        self.assertEqual(links[2], "http://wiki/track")

    def test_update_knowledge_graph(self):
        self.db.upsert_embedding("track_2", np.array([0.1, 0.2, 0.3]), "v1")
        self.db.link_knowledge_graph("track_2", mbid="mbid-123")
        self.db.link_knowledge_graph("track_2", mbid="mbid-456", spotify_id="spot-1")

        links = self.db.get_knowledge_graph_links("track_2")
        self.assertEqual(links[0], "mbid-456")
        self.assertEqual(links[1], "spot-1")

    def test_get_missing_links(self):
        links = self.db.get_knowledge_graph_links("missing_track")
        self.assertIsNone(links)


if __name__ == "__main__":
    unittest.main()
