import sqlite3
import logging

logger = logging.getLogger(__name__)


class PluginState:
    """
    Manages the enabled/disabled state of plugins using a SQLite database.
    """

    def __init__(self, db_path: str = "plugin_state.db") -> None:
        """
        Initialize the PluginState tracker.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """
        Initialize the SQLite database and create the tracking table if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plugin_state (
                        plugin_id TEXT PRIMARY KEY,
                        is_active INTEGER NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize PluginState database: {e}")

    def is_plugin_active(self, plugin_id: str) -> bool:
        """
        Check if a plugin is marked as active.
        Defaults to True if the plugin is not found in the state tracker.

        Args:
            plugin_id (str): The ID/name of the plugin.

        Returns:
            bool: True if active or not found, False if explicitly disabled.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT is_active FROM plugin_state WHERE plugin_id = ?", (plugin_id,)
                )
                row = cursor.fetchone()

                if row is None:
                    # Default behavior for new/unknown plugins is to be active
                    return True

                return bool(row[0])
        except sqlite3.Error as e:
            logger.error(f"Error querying plugin state for '{plugin_id}': {e}")
            return True  # Fail open to avoid breaking functionality

    def set_plugin_active(self, plugin_id: str, is_active: bool) -> None:
        """
        Update the active state of a plugin.

        Args:
            plugin_id (str): The ID/name of the plugin.
            is_active (bool): True to enable, False to disable.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO plugin_state (plugin_id, is_active)
                    VALUES (?, ?)
                    ON CONFLICT(plugin_id) DO UPDATE SET is_active = excluded.is_active
                    """,
                    (plugin_id, 1 if is_active else 0),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating plugin state for '{plugin_id}': {e}")
