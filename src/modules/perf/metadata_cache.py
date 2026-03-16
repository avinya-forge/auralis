"""
Auralis - Metadata Cache Module (Performance)

This module provides a persistent SQLite-based caching service specifically for
metadata with a 7-day Time-To-Live (TTL) expiration logic.
"""

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("auralis.perf.metadata_cache")


class MetadataCache:
    """
    Persistent metadata cache using SQLite.
    Implements a 7-day TTL expiration logic.

    Schema:
        metadata (
            hash TEXT PRIMARY KEY,
            json_data TEXT,
            last_updated REAL
        )
    """

    TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "MetadataCache":
        """Singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetadataCache, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        """Initialize the MetadataCache."""
        if getattr(self, "_initialized", False):
            return

        self.db_path = Path.home() / ".auralis" / "metadata_cache.db"
        self._init_db()
        self.clean_expired()  # Clean up old records on startup
        self._initialized = True

    def _init_db(self) -> None:
        """Initialize the database and create the table if it doesn't exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        hash TEXT PRIMARY KEY,
                        json_data TEXT,
                        last_updated REAL
                    )
                    """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing metadata cache database: {e}")

    def clean_expired(self) -> None:
        """Remove entries older than the 7-day TTL."""
        try:
            expiration_threshold = time.time() - self.TTL_SECONDS
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM metadata WHERE last_updated < ?", (expiration_threshold,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error cleaning expired cache records: {e}")

    def get(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a file hash. Expired records are ignored and lazily deleted.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            Optional[Dict[str, Any]]: The cached metadata, or None if not found or expired.
        """
        if not file_hash:
            return None

        try:
            current_time = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT json_data, last_updated FROM metadata WHERE hash = ?", (file_hash,)
                )
                row = cursor.fetchone()

                if row:
                    json_data, last_updated = row

                    # Check TTL (Lazy expiration)
                    if current_time - last_updated > self.TTL_SECONDS:
                        cursor.execute("DELETE FROM metadata WHERE hash = ?", (file_hash,))
                        conn.commit()
                        return None

                    return json.loads(json_data)  # type: ignore
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving metadata for hash {file_hash}: {e}")

        return None

    def set(self, file_hash: str, data: Dict[str, Any]) -> bool:
        """
        Save metadata for a file hash.

        Args:
            file_hash (str): The hash of the file.
            data (Dict[str, Any]): The metadata to cache.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not file_hash or not data:
            return False

        try:
            current_time = time.time()
            json_str = json.dumps(data)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO metadata (hash, json_data, last_updated)
                    VALUES (?, ?, ?)
                    """,
                    (file_hash, json_str, current_time),
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving metadata for hash {file_hash}: {e}")
            return False

    def close(self) -> None:
        """Close any resources."""
        pass
