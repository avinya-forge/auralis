"""
Auralis - Database Utilities
Standardized SQLite resource management.
"""

import contextlib
import sqlite3
from typing import Generator


@contextlib.contextmanager
def get_db_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for safe SQLite connection handling.
    Ensures connection is closed and transactions are committed/rolled back.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        # Standardize Microsecond Precision Timestamps
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
