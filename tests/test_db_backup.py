import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.modules.db.backup import backup_database
from src.services.cloud.provider_interface import CloudProviderInterface


class TestDBBackup(unittest.TestCase):
    def test_backup_database_uploads_existing_file(self):
        # Create a dummy file to represent the database
        fd, db_path = tempfile.mkstemp()
        os.close(fd)

        try:
            mock_provider = MagicMock(spec=CloudProviderInterface)
            mock_provider.name = "MockCloud"
            mock_provider.upload_file.return_value = True

            result = backup_database(db_path, mock_provider)

            self.assertTrue(result)
            filename = os.path.basename(db_path)
            mock_provider.upload_file.assert_called_once_with(db_path, f"backups/{filename}")

        finally:
            os.unlink(db_path)

    def test_backup_database_file_not_found(self):
        mock_provider = MagicMock(spec=CloudProviderInterface)
        result = backup_database("non_existent_db.sqlite", mock_provider)

        self.assertFalse(result)
        mock_provider.upload_file.assert_not_called()

    def test_backup_database_upload_fails(self):
        fd, db_path = tempfile.mkstemp()
        os.close(fd)

        try:
            mock_provider = MagicMock(spec=CloudProviderInterface)
            mock_provider.name = "MockCloud"
            mock_provider.upload_file.return_value = False

            result = backup_database(db_path, mock_provider)

            self.assertFalse(result)
            filename = os.path.basename(db_path)
            mock_provider.upload_file.assert_called_once_with(db_path, f"backups/{filename}")

        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
