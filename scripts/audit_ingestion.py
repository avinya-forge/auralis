#!/usr/bin/env python3
"""
Auralis - Ingestion Audit Script
Analyzes the state of the ingestion staging table.
"""

import sys
from src.utils.db_utils import get_db_connection


def audit_staging(db_path: str):
    """
    Prints a summary of staged records.
    """
    print(f"--- Ingestion Audit: {db_path} ---")
    try:
        with get_db_connection(db_path) as conn:
            # Check if table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ingestion_staging'"
            )
            if not cursor.fetchone():
                print("No ingestion_staging table found.")
                return

            # Success rate
            cursor = conn.execute("SELECT status, COUNT(*) FROM ingestion_staging GROUP BY status")
            rows = cursor.fetchall()
            if not rows:
                print("Staging table is empty.")
                return

            print("Record Status Summary:")
            for status, count in rows:
                print(f"  {status}: {count}")

    except Exception as e:
        print(f"Audit failed: {e}")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "cache.db"
    audit_staging(db)
