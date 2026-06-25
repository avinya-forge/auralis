"""
Auralis - Personal Listening Stats Aggregation
"""

import logging
from typing import Dict

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


def init_play_history_schema(db_path: str) -> None:
    """Initialize the play_history schema if it doesn't exist."""
    with get_db_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id TEXT NOT NULL,
                played_at TEXT NOT NULL
            )
        """
        )


class StatsAggregator:
    """
    Aggregates personal listening statistics.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        init_play_history_schema(self.db_path)

    def get_top_tracks(self, limit: int = 10) -> Dict[str, int]:
        """
        Retrieves the most played tracks and their play counts.
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT track_id, COUNT(*) as play_count
                    FROM play_history
                    GROUP BY track_id
                    ORDER BY play_count DESC
                    LIMIT ?
                """,
                    (limit,),
                )
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
        except Exception as e:
            logger.error(f"Failed to get top tracks: {e}")
            return {}
