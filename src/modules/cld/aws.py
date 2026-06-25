"""
Auralis - AWS S3 Cloud Provider
"""

import logging
from typing import Any, Dict, List

from src.services.cloud.provider_interface import CloudProviderInterface

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception

logger = logging.getLogger(__name__)


class AWSProvider(CloudProviderInterface):
    """AWS S3 implementation of CloudProviderInterface."""

    def __init__(self):
        self.s3_client = None
        self.bucket_name = None

    @property
    def name(self) -> str:
        return "AWS S3"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        if not BOTO3_AVAILABLE:
            logger.error("boto3 is not installed.")
            return False

        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=credentials.get('access_key'),
                aws_secret_access_key=credentials.get('secret_key'),
                region_name=credentials.get('region', 'us-east-1')
            )
            self.bucket_name = credentials.get('bucket_name')
            if not self.bucket_name:
                return False

            # Verify credentials by listing buckets or checking if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            logger.error(f"AWS authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during AWS authentication: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        if not self.s3_client or not self.bucket_name:
            return False
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, remote_path)
            return True
        except ClientError as e:
            logger.error(f"AWS upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        if not self.s3_client or not self.bucket_name:
            return False
        try:
            self.s3_client.download_file(self.bucket_name, remote_path, local_path)
            return True
        except ClientError as e:
            logger.error(f"AWS download failed: {e}")
            return False

    def list_files(self, remote_prefix: str = "") -> List[Dict[str, Any]]:
        if not self.s3_client or not self.bucket_name:
            return []
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=remote_prefix)
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'path': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'hash': obj['ETag'].strip('"')
                    })
            return files
        except ClientError as e:
            logger.error(f"AWS list files failed: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        if not self.s3_client or not self.bucket_name:
            return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except ClientError as e:
            logger.error(f"AWS delete file failed: {e}")
            return False

    def get_quota(self) -> Dict[str, Any]:
        """AWS S3 doesn't have a simple quota API like Drive, so return dummy values."""
        if not self.s3_client:
            return {'used': 0, 'total': 0}
        return {'used': -1, 'total': -1}
