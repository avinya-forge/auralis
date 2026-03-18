import os
import sqlite3
from typing import Optional, Tuple


class OfflineCache:
    def __init__(self, db_path: str, max_size_bytes: int) -> None:
        self.db_path = db_path
        self.max_size_bytes = max_size_bytes
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mobile_tracks (
                id TEXT PRIMARY KEY,
                title TEXT,
                artist TEXT,
                local_path TEXT,
                file_size INTEGER,
                last_accessed TIMESTAMP
            )
        """
        )
        self.conn.commit()

    def get_total_size(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(file_size) FROM mobile_tracks")
        result = cursor.fetchone()[0]
        return result if result is not None else 0

    def cache_track(
        self, track_id: str, title: str, artist: str, file_path: str, file_size: int
    ) -> None:
        self._enforce_lru(file_size)
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO mobile_tracks (id, title, artist, local_path, file_size, last_accessed)
            VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))
        """,
            (track_id, title, artist, file_path, file_size),
        )
        self.conn.commit()

    def get_track(self, track_id: str) -> Optional[Tuple[str, str, str, str, int]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE mobile_tracks
            SET last_accessed = strftime('%Y-%m-%d %H:%M:%f', 'now')
            WHERE id = ?
        """,
            (track_id,),
        )
        self.conn.commit()

        cursor.execute(
            """
            SELECT id, title, artist, local_path, file_size
            FROM mobile_tracks
            WHERE id = ?
        """,
            (track_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return (row[0], row[1], row[2], row[3], row[4])

    def _enforce_lru(self, incoming_size: int) -> None:
        cursor = self.conn.cursor()
        while self.get_total_size() + incoming_size > self.max_size_bytes:
            cursor.execute(
                "SELECT id, local_path FROM mobile_tracks ORDER BY last_accessed ASC LIMIT 1"
            )
            oldest = cursor.fetchone()
            if oldest:
                track_id, local_path = oldest
                if os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except OSError:
                        pass
                cursor.execute("DELETE FROM mobile_tracks WHERE id=?", (track_id,))
                self.conn.commit()
            else:
                break

    def clear_cache(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT local_path FROM mobile_tracks")
        for (local_path,) in cursor.fetchall():
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except OSError:
                    pass
        cursor.execute("DELETE FROM mobile_tracks")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
