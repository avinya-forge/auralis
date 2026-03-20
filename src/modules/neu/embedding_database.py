import logging
import sqlite3
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingDatabase:
    """
    Lightweight SQLite adapter to store and query track vectors.
    """

    def __init__(self, db_path: str = "embeddings.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        track_id VARCHAR PRIMARY KEY,
                        vector_blob BLOB,
                        model_version VARCHAR
                    )
                    """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def upsert_embedding(self, track_id: str, vector: np.ndarray, model_version: str) -> None:
        """
        Insert or update a track vector.

        Args:
            track_id: Unique identifier for the track.
            vector: Numpy array representing the track embedding.
            model_version: The version of the model used to generate the embedding.
        """
        try:
            # Enforce np.float32 array as per system requirements to avoid division-by-zero or memoryview type errors
            vector_float32 = vector.astype(np.float32)
            vector_blob = vector_float32.tobytes()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO embeddings (track_id, vector_blob, model_version)
                    VALUES (?, ?, ?)
                    ON CONFLICT(track_id) DO UPDATE SET
                        vector_blob = excluded.vector_blob,
                        model_version = excluded.model_version
                    """,
                    (track_id, vector_blob, model_version),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error during upsert_embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during upsert_embedding: {e}")
            raise

    def get_embedding(self, track_id: str) -> Optional[np.ndarray]:
        """
        Retrieve a track vector by its ID.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT vector_blob FROM embeddings WHERE track_id = ?", (track_id,))
                row = cursor.fetchone()

                if row:
                    blob = row[0]
                    return np.frombuffer(blob, dtype=np.float32)
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error during get_embedding: {e}")
            return None

    def search_similar(
        self, target_embedding: np.ndarray, top_k: int = 5, model_version: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Find similar tracks using cosine similarity.

        Args:
            target_embedding: The numpy array of the target track's embedding.
            top_k: Number of similar tracks to return.
            model_version: Optional model version to filter by.

        Returns:
            A list of tuples containing (track_id, similarity_score).
        """
        try:
            target_float32 = target_embedding.astype(np.float32)
            # Normalize target vector for cosine similarity
            target_norm = np.linalg.norm(target_float32)
            if target_norm == 0:
                logger.warning(
                    "Target embedding has zero norm, cannot calculate cosine similarity."
                )
                return []

            query = "SELECT track_id, vector_blob FROM embeddings"
            params = []

            if model_version:
                query += " WHERE model_version = ?"
                params.append(model_version)

            results = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))

                for row in cursor.fetchall():
                    track_id = row[0]
                    blob = row[1]
                    vector = np.frombuffer(blob, dtype=np.float32)

                    vector_norm = np.linalg.norm(vector)
                    if vector_norm == 0:
                        continue

                    # Calculate cosine similarity
                    similarity = np.dot(target_float32, vector) / (target_norm * vector_norm)
                    results.append((track_id, float(similarity)))

            # Sort by similarity descending
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        except sqlite3.Error as e:
            logger.error(f"Database error during search_similar: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during search_similar: {e}")
            return []
