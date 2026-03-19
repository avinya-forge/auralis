import logging
import sqlite3
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingDatabase:
    """
    A lightweight SQLite database wrapper to store and query track embedding vectors.
    """

    def __init__(self, db_path: str = "embeddings.db"):
        """
        Initializes the EmbeddingDatabase.

        Args:
            db_path (str): The path to the SQLite database. Use ":memory:" for in-memory db.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Creates the embeddings table if it does not exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    track_id VARCHAR PRIMARY KEY,
                    vector_blob BLOB NOT NULL,
                    model_version VARCHAR NOT NULL
                )
                """)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create embeddings table: {e}")
            raise

    def upsert_embedding(self, track_id: str, vector: np.ndarray, model_version: str) -> None:
        """
        Inserts or updates an embedding vector for a given track.

        Args:
            track_id (str): The unique identifier for the track.
            vector (np.ndarray): The embedding vector.
            model_version (str): The version of the model used to generate the embedding.
        """
        try:
            # Ensure the vector is converted to bytes for storage
            vector = vector.astype(np.float32)
            vector_blob = vector.tobytes()

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO embeddings (track_id, vector_blob, model_version)
                VALUES (?, ?, ?)
                ON CONFLICT(track_id) DO UPDATE SET
                    vector_blob=excluded.vector_blob,
                    model_version=excluded.model_version
                """,
                (track_id, vector_blob, model_version),
            )
            self.conn.commit()
            logger.debug(f"Upserted embedding for track_id: {track_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to upsert embedding for track_id {track_id}: {e}")
            self.conn.rollback()
            raise

    def search_similar(
        self, target_vector: np.ndarray, top_k: int = 5, model_version: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Finds the top_k most similar tracks to the target_vector using cosine similarity.

        Args:
            target_vector (np.ndarray): The target embedding vector.
            top_k (int): The number of top results to return.
            model_version (str, optional): Filter by model_version if provided.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing (track_id, similarity_score).
        """
        try:
            cursor = self.conn.cursor()

            if model_version:
                cursor.execute(
                    "SELECT track_id, vector_blob FROM embeddings WHERE model_version = ?",
                    (model_version,),
                )
            else:
                cursor.execute("SELECT track_id, vector_blob FROM embeddings")

            results = []

            # Compute norm of target vector once
            target_norm = np.linalg.norm(target_vector)

            # Prevent division by zero if target vector is all zeros
            if target_norm == 0:
                logger.warning("Target vector has zero norm. Cosine similarity will be 0.")
                target_norm = 1e-10

            for row in cursor.fetchall():
                track_id, vector_blob = row
                # We assume float32 here. If another dtype is used, it must be specified
                vector = np.frombuffer(vector_blob, dtype=np.float32)

                vector_norm = np.linalg.norm(vector)
                if vector_norm == 0:
                    continue  # Ignore zero vectors in db

                # Compute cosine similarity
                dot_product = np.dot(target_vector, vector)
                similarity = dot_product / (target_norm * vector_norm)

                results.append((track_id, float(similarity)))

            # Sort by similarity score descending
            results.sort(key=lambda x: x[1], reverse=True)

            return results[:top_k]

        except sqlite3.Error as e:
            logger.error(f"Database error during search_similar: {e}")
            raise

    def close(self) -> None:
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
