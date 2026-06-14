"""
data-cleanup-orphans: Cleanup track metadata with missing local/cloud files
"""

import logging
import os

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


def cleanup_orphaned_metadata(db_path: str) -> int:
    """
    Scans the mobile_tracks table for local_paths that do not exist
    on the filesystem and atomically deletes those orphaned records.

    Returns the number of removed orphans.
    """
    removed_count = 0
    try:
        with get_db_connection(db_path) as conn:
            # We first fetch all paths to minimize lock time
            cursor = conn.execute("SELECT id, local_path FROM mobile_tracks")
            tracks = cursor.fetchall()

            orphans = []
            for track_id, local_path in tracks:
                if local_path and not os.path.exists(local_path):
                    orphans.append((track_id,))

            if orphans:
                # Atomically delete orphans
                conn.executemany("DELETE FROM mobile_tracks WHERE id = ?", orphans)
                removed_count = len(orphans)
                logger.info(f"Removed {removed_count} orphaned tracks from mobile cache.")
            else:
                logger.info("No orphaned tracks found.")

    except Exception as e:
        logger.error(f"Failed to cleanup orphaned metadata in {db_path}: {e}")
        raise

    return removed_count
