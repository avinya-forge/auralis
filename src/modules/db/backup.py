"""
Auralis - Automated Database Backups
Handles uploading database backups to cloud providers.
"""

import logging
import os
from src.services.cloud.provider_interface import CloudProviderInterface

logger = logging.getLogger(__name__)


def backup_database(db_path: str, provider: CloudProviderInterface) -> bool:
    """
    Backs up a local SQLite database to a cloud provider.

    Args:
        db_path: Path to the local database file.
        provider: Instance of a CloudProviderInterface implementation.

    Returns:
        True if the backup was successful, False otherwise.
    """
    if not os.path.exists(db_path):
        logger.error(f"Database backup failed: File not found {db_path}")
        return False

    try:
        filename = os.path.basename(db_path)
        remote_path = f"backups/{filename}"

        success = provider.upload_file(db_path, remote_path)

        if success:
            logger.info(f"Successfully backed up {db_path} to {provider.name} at {remote_path}")
            return True
        else:
            logger.error(f"Failed to backup {db_path} to {provider.name}")
            return False

    except Exception as e:
        logger.error(f"Unexpected error during database backup: {e}")
        return False
