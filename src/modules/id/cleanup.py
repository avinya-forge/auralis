"""
Auralis - Play History Cleanup Module
Prunes play history older than a configurable limit.
"""

import logging
from datetime import datetime, timedelta

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


def init_play_history_schema(db_path: str) -> None:
    """Initialize the play_history schema if it doesn't exist to prevent errors."""
    with get_db_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id TEXT NOT NULL,
                played_at TEXT NOT NULL
            )
        """)


def prune_play_history(db_path: str, days_old: int = 365) -> int:
    """
    Prunes play history records older than the specified number of days.
    Relies on microsecond precision timestamps.

    Args:
        db_path: Path to the SQLite database.
        days_old: Number of days before which history is deleted.

    Returns:
        Number of deleted rows.
    """
    # Ensure schema exists first
    init_play_history_schema(db_path)

    cutoff_date = datetime.now() - timedelta(days=days_old)
    # Match the Auralis standard microsecond precision format
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S.%f")

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM play_history WHERE played_at < ?", (cutoff_str,))
            deleted_count = cursor.rowcount
            logger.info(f"Pruned {deleted_count} play history records older than {days_old} days.")
            return deleted_count
    except Exception as e:
        logger.error(f"Failed to prune play history: {e}")
        return 0
