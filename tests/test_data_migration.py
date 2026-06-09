import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.utils.db_utils import get_db_connection
except ImportError:
    pass


@pytest.fixture
def test_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    with get_db_connection(db_path) as conn:
        conn.execute("CREATE TABLE tracks (id TEXT PRIMARY KEY);")
        conn.execute("INSERT INTO tracks (id) VALUES ('track_1');")
        with open("resources/db/schema_expansion_v2.sql", "r") as f:
            conn.executescript(f.read())
    yield db_path


def test_v2_migration(test_db):
    with get_db_connection(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO v2_metadata (track_id, gharana, instrument) VALUES ('track_1', 'Agra', 'Sitar');"
        )
        cursor.execute(
            "SELECT track_id, gharana, instrument FROM v2_metadata WHERE track_id='track_1';"
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "track_1"
        assert row[1] == "Agra"
        assert row[2] == "Sitar"
