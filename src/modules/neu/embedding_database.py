"""
Auralis - Embedding Database Module
"""

import logging
from typing import List, Optional, Tuple

import numpy as np

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


class EmbeddingDatabase:
    """
    Lightweight SQLite adapter to store and query track vectors.
    """

    def __init__(self, db_path: str = "embeddings.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        try:
            with get_db_connection(self.db_path) as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        track_id VARCHAR PRIMARY KEY,
                        vector_blob BLOB,
                        model_version VARCHAR
                    );
                    CREATE TABLE IF NOT EXISTS knowledge_graph_links (
                        track_id VARCHAR PRIMARY KEY,
                        mbid VARCHAR,
                        spotify_id VARCHAR,
                        wikipedia_url VARCHAR,
                        FOREIGN KEY(track_id) REFERENCES embeddings(track_id)
                    );
                    """)
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def link_knowledge_graph(
        self,
        track_id: str,
        mbid: Optional[str] = None,
        spotify_id: Optional[str] = None,
        wikipedia_url: Optional[str] = None,
    ) -> None:
        """Link a track embedding to external knowledge graph nodes."""
        try:
            with get_db_connection(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO knowledge_graph_links (track_id, mbid, spotify_id, wikipedia_url)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(track_id) DO UPDATE SET
                        mbid = excluded.mbid,
                        spotify_id = excluded.spotify_id,
                        wikipedia_url = excluded.wikipedia_url
                    """,
                    (track_id, mbid, spotify_id, wikipedia_url),
                )
        except Exception as e:
            logger.error(f"Error linking knowledge graph: {e}")
            raise

    def get_knowledge_graph_links(self, track_id: str) -> Optional[tuple]:
        """Retrieve knowledge graph links for a track."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT mbid, spotify_id, wikipedia_url FROM knowledge_graph_links WHERE track_id = ?",
                    (track_id,),
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error retrieving knowledge graph links: {e}")
            return None

    def upsert_embedding(self, track_id: str, vector: np.ndarray, model_version: str) -> None:
        """Insert or update a track vector."""
        try:
            vector_float32 = vector.astype(np.float32)
            vector_blob = vector_float32.tobytes()

            with get_db_connection(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO embeddings (track_id, vector_blob, model_version)
                    VALUES (?, ?, ?)
                    ON CONFLICT(track_id) DO UPDATE SET
                        vector_blob = excluded.vector_blob,
                        model_version = excluded.model_version
                    """,
                    (track_id, vector_blob, model_version),
                )
        except Exception as e:
            logger.error(f"Error during upsert_embedding: {e}")
            raise

    def get_embedding(self, track_id: str) -> Optional[np.ndarray]:
        """Retrieve a track vector by its ID."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT vector_blob FROM embeddings WHERE track_id = ?", (track_id,)
                )
                row = cursor.fetchone()
                if row:
                    return np.frombuffer(row[0], dtype=np.float32)
                return None
        except Exception as e:
            logger.error(f"Error during get_embedding: {e}")
            return None

    def search_similar(
        self, target_embedding: np.ndarray, top_k: int = 5, model_version: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Find similar tracks using cosine similarity."""
        try:
            target_float32 = target_embedding.astype(np.float32)
            target_norm = np.linalg.norm(target_float32)
            if target_norm == 0:
                return []

            query = "SELECT track_id, vector_blob FROM embeddings"
            params = []
            if model_version:
                query += " WHERE model_version = ?"
                params.append(model_version)

            results = []
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute(query, tuple(params))
                for track_id, blob in cursor.fetchall():
                    vector = np.frombuffer(blob, dtype=np.float32)
                    vector_norm = np.linalg.norm(vector)
                    if vector_norm == 0:
                        continue
                    similarity = np.dot(target_float32, vector) / (target_norm * vector_norm)
                    results.append((track_id, float(similarity)))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error during search_similar: {e}")
            return []
