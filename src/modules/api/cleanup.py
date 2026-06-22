import datetime
import logging

from src.utils.db_utils import get_db_connection

logger = logging.getLogger(__name__)


def prune_expired_tokens(db_path: str):
    """
    Prune expired JWT tokens and invalid session routes from the database.
    Cron-safe.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%f")

    try:
        with get_db_connection(db_path) as conn:
            # Create table if it doesn't exist for mock purposes/cron resilience
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    token TEXT,
                    expires_at TEXT
                )
            """
            )

            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (current_time,))
            deleted_count = cursor.rowcount
            logger.info(f"Pruned {deleted_count} expired session(s).")
            return deleted_count
    except Exception as e:
        logger.error(f"Error pruning expired tokens: {e}")
        return 0
