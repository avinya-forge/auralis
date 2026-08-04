import os
import sqlite3
import pytest
from unittest.mock import MagicMock
from src.modules.cld.sync_state_tracker import SyncStateTracker
from src.services.cloud.provider_interface import CloudProviderInterface

def test_edge_cloud_handoff_integration(tmp_path):
    # Setup test DB
    db_path = str(tmp_path / "sync_state_test.db")
    tracker = SyncStateTracker(db_path=db_path)

    # Mock Cloud Provider
    mock_provider = MagicMock(spec=CloudProviderInterface)
    mock_provider.upload_file.return_value = True

    file_hash = "mock_hash_12345"
    remote_id = "mock_remote_id_67890"

    # Simulate upload
    success = mock_provider.upload_file("/local/path", "/remote/path")
    assert success is True

    # Record upload in tracker
    tracker.record_upload(file_hash, remote_id)

    # Verify tracker state
    assert tracker.is_uploaded(file_hash) is True

    # Ensure it returns false for an unknown file
    assert tracker.is_uploaded("unknown_hash") is False

    # Test DB integrity
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT remote_id FROM sync_state WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == remote_id
