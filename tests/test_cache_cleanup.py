from pathlib import Path
from typing import Generator

import pytest

from src.services.cache.cleanup import cleanup_orphaned_metadata
from src.utils.db_utils import get_db_connection


@pytest.fixture
def mock_db_with_orphans(tmp_path: Path) -> Generator[str, None, None]:
    db_path = str(tmp_path / "offline_cache.db")

    # Create valid dummy files
    valid_file1 = tmp_path / "track1.mp3"
    valid_file1.write_text("dummy audio data")
    valid_file2 = tmp_path / "track2.mp3"
    valid_file2.write_text("dummy audio data")

    with get_db_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mobile_tracks (
                id TEXT PRIMARY KEY,
                title TEXT,
                artist TEXT,
                local_path TEXT,
                file_size INTEGER,
                last_accessed TIMESTAMP
            )
            """
        )

        # Insert 2 valid tracks and 2 orphans
        tracks = [
            ("id1", "Valid1", "Artist", str(valid_file1), 100, "2024-01-01 00:00:00.000000"),
            ("id2", "Valid2", "Artist", str(valid_file2), 100, "2024-01-01 00:00:00.000000"),
            (
                "id3",
                "Orphan1",
                "Artist",
                str(tmp_path / "missing1.mp3"),
                100,
                "2024-01-01 00:00:00.000000",
            ),
            (
                "id4",
                "Orphan2",
                "Artist",
                str(tmp_path / "missing2.mp3"),
                100,
                "2024-01-01 00:00:00.000000",
            ),
        ]
        conn.executemany(
            "INSERT INTO mobile_tracks (id, title, artist, local_path, file_size, last_accessed) VALUES (?, ?, ?, ?, ?, ?)",
            tracks,
        )

    yield db_path


def test_cleanup_orphaned_metadata(mock_db_with_orphans: str) -> None:
    # Action: Run cleanup
    removed_count = cleanup_orphaned_metadata(mock_db_with_orphans)

    # Assert correct number of orphans removed
    assert removed_count == 2

    # Assert only valid tracks remain
    with get_db_connection(mock_db_with_orphans) as conn:
        cursor = conn.execute("SELECT id FROM mobile_tracks")
        remaining_ids = {row[0] for row in cursor.fetchall()}

    assert remaining_ids == {"id1", "id2"}
