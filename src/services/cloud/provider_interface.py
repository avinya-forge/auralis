"""
Auralis - Cloud Provider Interface

This module defines the abstract base class for cloud sync providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class CloudProviderInterface(ABC):
    """
    Abstract base class defining the contract for cloud storage providers
    in the Auralis Cloud Sync Engine.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the cloud provider."""
        pass

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with the cloud provider.

        Args:
            credentials: A dictionary containing provider-specific credentials.

        Returns:
            True if authentication is successful, False otherwise.
        """
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a local file to the cloud.

        Args:
            local_path: Path to the local file.
            remote_path: Target path in the cloud.

        Returns:
            True if upload is successful, False otherwise.
        """
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from the cloud to the local filesystem.

        Args:
            remote_path: Path of the file in the cloud.
            local_path: Target local path to save the file.

        Returns:
            True if download is successful, False otherwise.
        """
        pass

    @abstractmethod
    def list_files(self, remote_prefix: str = "") -> List[Dict[str, Any]]:
        """
        List files in the cloud storage.

        Args:
            remote_prefix: Optional prefix/folder to list files from.

        Returns:
            A list of dictionaries containing file metadata (e.g., path, size, hash, last_modified).
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from the cloud storage.

        Args:
            remote_path: Path of the file to delete.

        Returns:
            True if deletion is successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_quota(self) -> Dict[str, Any]:
        """
        Get the storage quota information from the provider.

        Returns:
            A dictionary containing quota details (e.g., 'used', 'total').
        """
        pass
