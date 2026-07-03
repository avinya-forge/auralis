"""
Auralis - Database Cleanup
Handles removing orphaned metadata entries.
"""

import json
import logging
import os
from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


def cleanup_orphaned_metadata(db_path: str) -> int:
    """
    Cleans up metadata entries from the database if the associated file
    no longer exists on disk.

    Args:
        db_path: Path to the SQLite database.

    Returns:
        Number of orphaned entries removed.
    """
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}")
        return 0

    orphans = []

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.execute("SELECT file_hash, data FROM metadata")
            rows = cursor.fetchall()

            for file_hash, data_str in rows:
                if not data_str:
                    continue

                try:
                    data = json.loads(data_str)
                    # Check for path keys
                    path = data.get("path") or data.get("file_path")
                    if path and not os.path.exists(path):
                        orphans.append(file_hash)
                except json.JSONDecodeError:
                    # If it's corrupted, we might consider it orphaned too
                    # but for safety, we skip
                    continue

            if orphans:
                # Delete orphaned rows
                conn.executemany(
                    "DELETE FROM metadata WHERE file_hash = ?", [(h,) for h in orphans]
                )
                logger.info(f"Cleaned up {len(orphans)} orphaned metadata entries.")

        return len(orphans)
    except Exception as e:
        logger.error(f"Error during orphaned metadata cleanup: {e}")
        return 0
