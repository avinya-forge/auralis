"""
Auralis - Profile Sync Module
"""

import json
import logging
import os
from typing import Any, Dict, List

from src.utils.db_utils import get_db_connection
from src.modules.id.stats import init_play_history_schema

logger = logging.getLogger(__name__)


class ProfileSync:
    """
    Handles export and import of personal profile data.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        init_play_history_schema(self.db_path)

    def export_profile(self, output_json_path: str) -> bool:
        """
        Exports the play history profile to a JSON file.
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT track_id, played_at FROM play_history")
                rows = cursor.fetchall()

            history = [{"track_id": row[0], "played_at": row[1]} for row in rows]
            profile_data = {"play_history": history}

            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)

            logger.info(f"Successfully exported profile to {output_json_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export profile: {e}")
            return False

    def import_profile(self, input_json_path: str) -> bool:
        """
        Imports the play history profile from a JSON file.
        """
        if not os.path.exists(input_json_path):
            logger.error(f"Import file does not exist: {input_json_path}")
            return False

        try:
            with open(input_json_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)

            history = profile_data.get("play_history", [])
            if not history:
                return True

            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                for item in history:
                    cursor.execute(
                        "INSERT INTO play_history (track_id, played_at) VALUES (?, ?)",
                        (item.get("track_id"), item.get("played_at"))
                    )

            logger.info(f"Successfully imported profile from {input_json_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return False
