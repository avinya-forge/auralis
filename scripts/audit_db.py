#!/usr/bin/env python3
"""
data-audit-integrity: Implement referential integrity check for the music graph
"""

import argparse
import logging
import sys
from typing import List

from src.utils.db_utils import get_db_connection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def audit_integrity(db_path: str) -> List[tuple]:
    """Check database referential integrity using PRAGMA foreign_key_check."""
    violations = []
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.execute("PRAGMA foreign_key_check;")
            violations = cursor.fetchall()

            if violations:
                logger.error(f"Integrity violations found in {db_path}:")
                for violation in violations:
                    # table, rowid, parent, fkid
                    logger.error(f"  Table: {violation[0]}, RowID: {violation[1]}, Parent: {violation[2]}, FKID: {violation[3]}")
            else:
                logger.info(f"Database {db_path} passed integrity check.")
    except Exception as e:
        logger.error(f"Failed to audit database {db_path}: {e}")
        raise

    return violations

def main():
    parser = argparse.ArgumentParser(description="Audit database referential integrity")
    parser.add_argument("db_path", help="Path to the SQLite database to audit")
    args = parser.parse_args()

    try:
        violations = audit_integrity(args.db_path)
        if violations:
            sys.exit(1)
        sys.exit(0)
    except Exception:
        sys.exit(2)

if __name__ == "__main__":
    main()
