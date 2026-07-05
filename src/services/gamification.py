"""
Auralis - Gamification Service
Handles user scoring and achievements for crowdsourcing tasks.
"""

import logging
from typing import Dict

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


class GamificationService:
    """
    Manages points and level progression for users.
    """

    POINTS_PER_VALIDATION = 10
    LEVEL_THRESHOLD = 100

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the user stats table."""
        with get_db_connection(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    validations_count INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1
                )
            """
            )

    def add_validation_points(self, user_id: str) -> Dict[str, int]:
        """
        Adds points for a successful validation and checks for level up.
        Returns the updated stats.
        """
        with get_db_connection(self.db_path) as conn:
            # Atomic update
            conn.execute(
                """
                INSERT INTO user_stats (user_id, points, validations_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    points = points + ?,
                    validations_count = validations_count + 1
            """,
                (user_id, self.POINTS_PER_VALIDATION, self.POINTS_PER_VALIDATION),
            )

            # Fetch and update level
            cursor = conn.execute("SELECT points FROM user_stats WHERE user_id = ?", (user_id,))
            points = cursor.fetchone()[0]
            new_level = (points // self.LEVEL_THRESHOLD) + 1

            conn.execute("UPDATE user_stats SET level = ? WHERE user_id = ?", (new_level, user_id))

            return {"points": points, "level": new_level}

    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """Retrieves user stats."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT points, level, validations_count FROM user_stats WHERE user_id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return {"points": row[0], "level": row[1], "validations": row[2]}
            return {"points": 0, "level": 1, "validations": 0}
