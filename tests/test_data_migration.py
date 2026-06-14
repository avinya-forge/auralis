import os
from pathlib import Path

from src.utils.db_utils import get_db_connection, run_migration


def test_schema_migration(tmp_path: Path) -> None:
    db_path = str(tmp_path / "test_migration.db")
    sql_path = "resources/db/schema_expansion_v2.sql"

    # Pre-create a dummy DB to test backup creation
    with get_db_connection(db_path) as conn:
        conn.execute("CREATE TABLE dummy (id INTEGER)")

    # Run migration
    run_migration(db_path, sql_path)

    # Verify backup was created
    backup_path = f"{db_path}.bak"
    assert os.path.exists(backup_path)

    # Verify tables exist
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            "dummy",
            "instruments",
            "gharanas",
            "track_instruments",
            "track_gharanas",
            "vocalists",
            "track_vocalists",
        }
        assert expected_tables.issubset(tables)
