"""AWS S3 file storage implementation."""

import logging
import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from auth_app.services.file_service import FileStorage

logger = logging.getLogger(__name__)

# Lazy-load S3 client
_s3_client = None


def get_s3_client():
    """Get or create S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _s3_client


class S3FileStorage(FileStorage):
    """File storage using AWS S3."""

    def __init__(self):
        self.s3_client = get_s3_client()
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION

    def upload(self, filename: str, file_data: bytes, user_id: int) -> str:
        """
        Upload a file to S3 and return its public URL.

        Args:
            filename: Original filename
            file_data: File contents as bytes
            user_id: User uploading the file

        Returns:
            Public S3 URL of the uploaded file
        """
        try:
            # Generate unique file key with user_id and timestamp
            file_ext = os.path.splitext(filename)[1]
            user_id_str = str(user_id)
            unique_filename = f'{user_id_str}/{datetime.utcnow().timestamp()}_{uuid.uuid4()}{file_ext}'

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_data,
                ContentType=self._get_content_type(file_ext),
            )

            # Construct public URL
            url = f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}'
            logger.info(f'File uploaded to S3: {unique_filename}')

            return url

        except ClientError as e:
            logger.error(f'Error uploading file to S3: {str(e)}', exc_info=True)
            raise
        except Exception as e:
            logger.error(f'Unexpected error uploading file: {str(e)}', exc_info=True)
            raise

    def get_url(self, file_key: str) -> str:
        """
        Get the public URL for a file in S3.

        Args:
            file_key: S3 object key

        Returns:
            Public S3 URL
        """
        return f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}'

    @staticmethod
    def _get_content_type(file_ext: str) -> str:
        """Determine content type from file extension."""
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
        }
        return content_types.get(file_ext.lower(), 'application/octet-stream')
