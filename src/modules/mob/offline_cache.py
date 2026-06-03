import os
import sqlite3
import time
from typing import Optional, Tuple


class OfflineCache:
    """Manages offline caching of audio files and metadata."""

    def __init__(
        self,
        db_path: str = "cache/offline.db",
        max_size_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        self.db_path = db_path
        self.max_size_bytes = max_size_bytes
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the cache database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (id TEXT PRIMARY KEY, title TEXT, "
            "artist TEXT, path TEXT, size INTEGER, last_accessed REAL)"
        )
        conn.close()

    def cache_track(self, track_id: str, title: str, artist: str, path: str, size: int) -> None:
        """Add or update a track in the cache with LRU eviction."""
        conn = sqlite3.connect(self.db_path)

        # Check if already exists to adjust total size properly
        cursor = conn.execute("SELECT size FROM cache WHERE id = ?", (track_id,))
        row = cursor.fetchone()
        current_total = self.get_total_size()
        if row:
            current_total -= row[0]

        # Evict until there's space
        while current_total + size > self.max_size_bytes:
            cursor = conn.execute(
                "SELECT id, path, size FROM cache WHERE id != ? "
                "ORDER BY last_accessed ASC LIMIT 1",
                (track_id,),
            )
            evict_row = cursor.fetchone()
            if not evict_row:
                break
            try:
                if os.path.exists(evict_row[1]):
                    os.remove(evict_row[1])
            except OSError:
                pass
            conn.execute("DELETE FROM cache WHERE id = ?", (evict_row[0],))
            current_total -= evict_row[2]

        conn.execute(
            "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?, ?)",
            (track_id, title, artist, path, size, time.time()),
        )
        conn.commit()
        conn.close()

    def get_track(self, track_id: str) -> Optional[Tuple[str, str, str, str, int]]:
        """Retrieve a track and update its last_accessed time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, title, artist, path, size FROM cache WHERE id = ?",
            (track_id,),
        )
        row = cursor.fetchone()
        if row:
            conn.execute(
                "UPDATE cache SET last_accessed = ? WHERE id = ?",
                (time.time(), track_id),
            )
            conn.commit()
            conn.close()
            return (row[0], row[1], row[2], row[3], int(row[4]))
        conn.close()
        return None

    def get_total_size(self) -> int:
        """Get total cached size."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT SUM(size) FROM cache")
        row = cursor.fetchone()
        conn.close()
        return int(row[0] or 0)

    def clear_cache(self) -> None:
        """Clear cache."""
        conn = sqlite3.connect(self.db_path)
        for row in conn.execute("SELECT path FROM cache").fetchall():
            try:
                if os.path.exists(row[0]):
                    os.remove(row[0])
            except OSError:
                pass
        conn.execute("DELETE FROM cache")
        conn.commit()
        conn.close()

    def close(self) -> None:
        """Close."""
        pass
