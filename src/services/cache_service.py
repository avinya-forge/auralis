"""
Auralis - Cache Service Module

This module provides a SQLite-based caching service for metadata and analysis results.
"""

import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, Optional, cast

logger = logging.getLogger("auralis.cache")


class CacheService:
    """
    Service for caching metadata and analysis results using SQLite.

    Schema:
        metadata (
            file_hash TEXT PRIMARY KEY,
            data TEXT,
            last_updated REAL
        )
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "CacheService":
        """Singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        """Initialize the CacheService."""
        if getattr(self, "_initialized", False):
            return

        self.db_path = Path.home() / ".auralis" / "cache.db"
        self._init_db()
        self._initialized = True

    def _init_db(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        file_hash TEXT PRIMARY KEY,
                        data TEXT,
                        last_updated REAL
                    )
                    """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing cache database: {e}")

    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a file hash.

        Args:
            file_hash (str): The hash of the file.

        Returns:
            Optional[Dict[str, Any]]: The cached metadata, or None if not found.
        """
        if not file_hash:
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM metadata WHERE file_hash = ?", (file_hash,))
                row = cursor.fetchone()
                if row:
                    return cast(Dict[str, Any], json.loads(row[0]))
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving metadata for hash {file_hash}: {e}")

        return None

    def save_metadata(self, file_hash: str, data: Dict[str, Any]) -> bool:
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
            import time

            current_time = time.time()
            json_data = json.dumps(data)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO metadata (file_hash, data, last_updated)
                    VALUES (?, ?, ?)
                    """,
                    (file_hash, json_data, current_time),
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving metadata for hash {file_hash}: {e}")
            return False

    def close(self) -> None:
        """Close any resources (placeholder for connection pooling if added)."""
        pass
