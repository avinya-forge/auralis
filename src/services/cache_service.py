"""
Auralis - Cache Service Module

This module provides a SQLite-based caching service for metadata and analysis results.
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.db_utils import get_db_connection

logger = logging.getLogger("auralis.cache")


class CacheService:
    """
    Service for caching metadata and analysis results using SQLite.
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

        self.db_path = str(Path.home() / ".auralis" / "cache.db")
        self._init_db()
        self._initialized = True

    def _init_db(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            with get_db_connection(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS metadata (
                        file_hash TEXT PRIMARY KEY,
                        data TEXT,
                        last_updated REAL
                    )
                    """
                )
        except Exception as e:
            logger.error(f"Error initializing cache database: {e}")

    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file hash."""
        if not file_hash:
            return None

        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM metadata WHERE file_hash = ?", (file_hash,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])  # type: ignore
        except Exception as e:
            logger.error(f"Error retrieving metadata for hash {file_hash}: {e}")

        return None

    def save_metadata(self, file_hash: str, data: Dict[str, Any]) -> bool:
        """Save metadata for a file hash."""
        if not file_hash or not data:
            return False

        try:
            json_data = json.dumps(data)
            with get_db_connection(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO metadata (file_hash, data, last_updated)
                    VALUES (?, ?, ?)
                    """,
                    (file_hash, json_data, time.time()),
                )
            return True
        except Exception as e:
            logger.error(f"Error saving metadata for hash {file_hash}: {e}")
            return False

    def close(self) -> None:
        """Close any resources."""
        pass
