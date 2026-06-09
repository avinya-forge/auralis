import sqlite3


class StatsAggregator:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_total_listens(self) -> int:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM play_history")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError:
            return 0

    def get_most_played_track(self) -> str:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT track_id, COUNT(*) as play_count FROM play_history GROUP BY track_id ORDER BY play_count DESC LIMIT 1"
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.OperationalError:
            return None

    def get_listening_time(self) -> int:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT SUM(duration) FROM play_history")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError:
            return 0
