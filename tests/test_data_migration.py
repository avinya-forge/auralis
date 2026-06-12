import sqlite3
from pathlib import Path
from typing import Any

import pytest

from src.utils.db_utils import get_db_connection


def test_schema_migration(tmp_path: Path) -> None:
    db_path = str(tmp_path / "test_migration.db")
    with get_db_connection(db_path) as conn:
        with open("resources/db/schema_expansion_v2.sql", "r") as f:
            conn.executescript(f.read())

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            "instruments",
            "gharanas",
            "track_instruments",
            "track_gharanas",
            "vocalists",
            "track_vocalists",
        }
        assert expected_tables.issubset(tables)
