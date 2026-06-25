"""
Auralis - Google Drive Cloud Provider
"""

import logging
from typing import Any, Dict, List

from src.services.cloud.provider_interface import CloudProviderInterface

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    build = None
    Credentials = None
    MediaFileUpload = None
    MediaIoBaseDownload = None
    io = None

logger = logging.getLogger(__name__)


class GoogleDriveProvider(CloudProviderInterface):
    """Google Drive implementation of CloudProviderInterface."""

    def __init__(self):
        self.service = None

    @property
    def name(self) -> str:
        return "Google Drive"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        if not GOOGLE_API_AVAILABLE:
            logger.error("google-api-python-client is not installed.")
            return False

        try:
            creds = Credentials(
                token=credentials.get('token'),
                refresh_token=credentials.get('refresh_token'),
                token_uri=credentials.get('token_uri'),
                client_id=credentials.get('client_id'),
                client_secret=credentials.get('client_secret'),
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            self.service = build('drive', 'v3', credentials=creds)
            # Verify by fetching about info
            self.service.about().get(fields="user").execute()
            return True
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        if not self.service:
            return False
        try:
            # Note: For real gdrive, remote_path might need to be resolved to folder IDs.
            # Here we just use the name for simplicity in this dummy stub.
            file_metadata = {'name': remote_path}
            media = MediaFileUpload(local_path, resumable=True)
            self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return True
        except Exception as e:
            logger.error(f"Google Drive upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        if not self.service:
            return False
        try:
            # We assume remote_path is the file ID for simplicity.
            request = self.service.files().get_media(fileId=remote_path)
            with io.FileIO(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            return True
        except Exception as e:
            logger.error(f"Google Drive download failed: {e}")
            return False

    def list_files(self, remote_prefix: str = "") -> List[Dict[str, Any]]:
        if not self.service:
            return []
        try:
            # Simplistic listing, ignoring remote_prefix filtering for now
            results = self.service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name, size, modifiedTime)"
            ).execute()
            items = results.get('files', [])
            files = []
            for item in items:
                files.append({
                    'path': item.get('id'), # Using ID as path
                    'name': item.get('name'),
                    'size': int(item.get('size', 0)),
                    'last_modified': item.get('modifiedTime'),
                    'hash': '' # Etag / hash not directly mapped
                })
            return files
        except Exception as e:
            logger.error(f"Google Drive list files failed: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        if not self.service:
            return False
        try:
            # We assume remote_path is the file ID.
            self.service.files().delete(fileId=remote_path).execute()
            return True
        except Exception as e:
            logger.error(f"Google Drive delete file failed: {e}")
            return False

    def get_quota(self) -> Dict[str, Any]:
        if not self.service:
            return {'used': 0, 'total': 0}
        try:
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get('storageQuota', {})
            return {
                'used': int(quota.get('usage', 0)),
                'total': int(quota.get('limit', -1))
            }
        except Exception as e:
            logger.error(f"Google Drive get quota failed: {e}")
            return {'used': 0, 'total': 0}
