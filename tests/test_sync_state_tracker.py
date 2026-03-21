import os
import sqlite3
import pytest
from src.modules.cld.sync_state_tracker import SyncStateTracker


@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing a temporary database file path."""
    db_file = tmp_path / "test_sync_state.db"
    return str(db_file)


def test_init_db(temp_db):
    """Test that the database schema is correctly initialized."""
    tracker = SyncStateTracker(temp_db)

    assert os.path.exists(temp_db)

    # Verify schema
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_state'")
        table = cursor.fetchone()
        assert table is not None
        assert table[0] == "sync_state"

        # Verify columns
        cursor.execute("PRAGMA table_info(sync_state)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "file_hash" in columns
        assert "remote_id" in columns
        assert "last_sync_timestamp" in columns


def test_is_uploaded_initially_false(temp_db):
    """Test that a new file hash is not marked as uploaded."""
    tracker = SyncStateTracker(temp_db)
    assert not tracker.is_uploaded("hash_123")


def test_record_upload(temp_db):
    """Test recording an upload saves it to the database."""
    tracker = SyncStateTracker(temp_db)
    tracker.record_upload("hash_123", "remote_abc")

    assert tracker.is_uploaded("hash_123")

    # Verify the values in the DB
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT remote_id, last_sync_timestamp FROM sync_state WHERE file_hash = ?", ("hash_123",))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "remote_abc"
        assert row[1] is not None  # Timestamp is set


import time

def test_record_upload_update(temp_db):
    """Test updating an existing upload correctly overrides remote_id and timestamp."""
    tracker = SyncStateTracker(temp_db)
    tracker.record_upload("hash_123", "remote_abc")

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_sync_timestamp FROM sync_state WHERE file_hash = ?", ("hash_123",))
        initial_timestamp = cursor.fetchone()[0]

    # Update the record
    time.sleep(0.01)
    tracker.record_upload("hash_123", "remote_xyz")

    assert tracker.is_uploaded("hash_123")

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT remote_id, last_sync_timestamp FROM sync_state WHERE file_hash = ?", ("hash_123",))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "remote_xyz"
        assert row[1] != initial_timestamp  # Timestamp should be updated


def test_is_uploaded_empty_db(temp_db):
    """Test is_uploaded handles corrupted or unexpectedly empty db."""
    tracker = SyncStateTracker(temp_db)

    # Intentionally delete the table to simulate corruption
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE sync_state")
        conn.commit()

    # Should safely return False without raising
    assert not tracker.is_uploaded("hash_123")


def test_init_db_error_handling(tmp_path):
    """Test that initialization handles connection errors."""
    # Create a directory to cause connection failure (can't connect to a directory)
    bad_db = tmp_path / "bad_db_dir"
    bad_db.mkdir()

    with pytest.raises(RuntimeError) as exc_info:
        SyncStateTracker(str(bad_db))
    assert "Failed to initialize SyncStateTracker database" in str(exc_info.value)


def test_record_upload_error_handling(temp_db):
    """Test that recording an upload handles DB errors gracefully."""
    tracker = SyncStateTracker(temp_db)

    # Corrupt the table
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE sync_state")
        conn.commit()

    with pytest.raises(RuntimeError) as exc_info:
        tracker.record_upload("hash_123", "remote_abc")
    assert "Failed to record upload in SyncStateTracker" in str(exc_info.value)
