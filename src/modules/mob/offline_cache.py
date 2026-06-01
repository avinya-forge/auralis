"""
Auralis - Mobile Offline Cache
"""

import os
from typing import Optional, Tuple

from src.utils.db_utils import get_db_connection


class OfflineCache:
    """
    Handles local caching of tracks for mobile/offline use.
    """

    def __init__(self, db_path: str, max_size_bytes: int) -> None:
        self.db_path = db_path
        self.max_size_bytes = max_size_bytes
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the mobile tracks table."""
        with get_db_connection(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mobile_tracks (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    artist TEXT,
                    local_path TEXT,
                    file_size INTEGER,
                    last_accessed TIMESTAMP
                )
            """)

    def get_total_size(self) -> int:
        """Calculate total cached file size."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.execute("SELECT SUM(file_size) FROM mobile_tracks")
            result = cursor.fetchone()[0]
            return result if result is not None else 0

    def cache_track(
        self, track_id: str, title: str, artist: str, file_path: str, file_size: int
    ) -> None:
        """Cache a track and enforce LRU policy."""
        self._enforce_lru(file_size)
        with get_db_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mobile_tracks (id, title, artist, local_path, file_size, last_accessed)
                VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))
            """,
                (track_id, title, artist, file_path, file_size),
            )

    def get_track(self, track_id: str) -> Optional[Tuple[str, str, str, str, int]]:
        """Retrieve a track and update its access timestamp."""
        with get_db_connection(self.db_path) as conn:
            conn.execute(
                "UPDATE mobile_tracks SET last_accessed = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE id = ?",
                (track_id,),
            )
            cursor = conn.execute(
                "SELECT id, title, artist, local_path, file_size FROM mobile_tracks WHERE id = ?",
                (track_id,),
            )
            return cursor.fetchone()

    def _enforce_lru(self, incoming_size: int) -> None:
        """Evict oldest tracks until incoming size fits."""
        while self.get_total_size() + incoming_size > self.max_size_bytes:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id, local_path FROM mobile_tracks ORDER BY last_accessed ASC LIMIT 1"
                )
                oldest = cursor.fetchone()
                if not oldest:
                    break

                track_id, local_path = oldest
                if os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except OSError:
                        pass
                conn.execute("DELETE FROM mobile_tracks WHERE id=?", (track_id,))

    def clear_cache(self) -> None:
        """Clear all cached tracks."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.execute("SELECT local_path FROM mobile_tracks")
            for (local_path,) in cursor.fetchall():
                if os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except OSError:
                        pass
            conn.execute("DELETE FROM mobile_tracks")

    def close(self) -> None:
        """Resource cleanup."""
        pass
