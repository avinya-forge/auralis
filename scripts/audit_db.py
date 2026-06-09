import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utils.db_utils import get_db_connection

def audit_integrity(db_path: str):
    if not os.path.exists(db_path):
        return True

    issues = []
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_key_check;")
        issues = cursor.fetchall()

    if issues:
        return False
    return True
