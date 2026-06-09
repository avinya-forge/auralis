import sqlite3
from datetime import datetime, timedelta


class HistoryCleanup:
    def __init__(self, db_connection):
        self.db = db_connection

    def prune_old_history(self, days: int = 365):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM play_history WHERE played_at < ?", (cutoff_date,))
            self.db.commit()
            return cursor.rowcount
        except sqlite3.OperationalError:
            self.db.rollback()
            return 0
