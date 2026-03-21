import sqlite3
import contextlib
import os


class SyncStateTracker:
    """
    SQLite-based tracker for cloud sync state.
    Tracks file_hash, remote_id, and last_sync_timestamp to prevent duplicate uploads.
    """

    def __init__(self, db_path: str = "sync_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        try:
            with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sync_state (
                        file_hash TEXT PRIMARY KEY,
                        remote_id TEXT,
                        last_sync_timestamp TEXT
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize SyncStateTracker database: {e}")

    def is_uploaded(self, file_hash: str) -> bool:
        """
        Check if a file with the given hash has already been uploaded.

        Args:
            file_hash: The hash of the file.

        Returns:
            True if the file is tracked as uploaded, False otherwise.
        """
        try:
            with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM sync_state WHERE file_hash = ?", (file_hash,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error:
            # Handle empty or corrupted DB safely by returning False
            return False

    def record_upload(self, file_hash: str, remote_id: str) -> None:
        """
        Record a successful upload.

        Args:
            file_hash: The hash of the file.
            remote_id: The remote identifier returned by the cloud provider.
        """
        try:
            with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sync_state (file_hash, remote_id, last_sync_timestamp)
                    VALUES (?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))
                    ON CONFLICT(file_hash) DO UPDATE SET
                        remote_id = excluded.remote_id,
                        last_sync_timestamp = strftime('%Y-%m-%d %H:%M:%f', 'now')
                    """,
                    (file_hash, remote_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to record upload in SyncStateTracker: {e}")
