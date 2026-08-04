import os
from unittest.mock import MagicMock

from src.modules.db.backup import backup_database
from src.services.cloud.provider_interface import CloudProviderInterface


def test_edge_cloud_handoff_integration(tmp_path):
    # Setup test DB
    db_path = str(tmp_path / "sync_state_test.db")
    with open(db_path, "w") as f:
        f.write("mock db content")

    # Mock Cloud Provider
    mock_provider = MagicMock(spec=CloudProviderInterface)
    mock_provider.name = "MockCloudProvider"
    mock_provider.upload_file.return_value = True

    # Simulate database backup orchestration
    success = backup_database(db_path, mock_provider)

    assert success is True
    # Verify that the correct orchestration happens via CloudProviderInterface
    remote_path = f"backups/{os.path.basename(db_path)}"
    mock_provider.upload_file.assert_called_once_with(db_path, remote_path)


def test_edge_cloud_handoff_integration_missing_file():
    mock_provider = MagicMock(spec=CloudProviderInterface)

    # Should fail due to missing DB
    success = backup_database("/invalid/path/db.sqlite", mock_provider)
    assert success is False
    mock_provider.upload_file.assert_not_called()


def test_edge_cloud_handoff_integration_upload_failure(tmp_path):
    db_path = str(tmp_path / "sync_state_test.db")
    with open(db_path, "w") as f:
        f.write("mock db content")

    mock_provider = MagicMock(spec=CloudProviderInterface)
    mock_provider.name = "MockCloudProvider"
    mock_provider.upload_file.return_value = False

    success = backup_database(db_path, mock_provider)
    assert success is False
    mock_provider.upload_file.assert_called_once()
