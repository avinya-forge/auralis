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


def run_migration(db_path: str, sql_path: str) -> None:
    """
    Safely execute a schema migration SQL script against a database,
    first creating a .bak backup for safety.
    """
    import logging
    import os
    import shutil

    logger = logging.getLogger(__name__)

    # 1. Create a backup
    if os.path.exists(db_path):
        backup_path = f"{db_path}.bak"
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"Created database backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create database backup before migration: {e}")
            raise

    # 2. Read SQL
    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
    except Exception as e:
        logger.error(f"Failed to read SQL script {sql_path}: {e}")
        raise

    # 3. Execute
    try:
        with get_db_connection(db_path) as conn:
            conn.executescript(sql_script)
            logger.info(f"Successfully ran migration script {sql_path} on {db_path}")
    except Exception as e:
        logger.error(f"Migration execution failed on {db_path}: {e}")
        raise
