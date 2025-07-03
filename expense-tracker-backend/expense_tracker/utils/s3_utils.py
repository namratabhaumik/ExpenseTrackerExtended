import boto3
import uuid
import os
from datetime import datetime
from django.conf import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class S3Handler:
    """Handle S3 operations for receipt uploads."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file_data, file_name, user_id):
        """
        Upload a file to S3.

        Args:
            file_data: Base64 encoded file data
            file_name: Original file name
            user_id: User ID for organizing files

        Returns:
            dict: Contains file_url, file_key, and success status
        """
        try:
            import base64

            # Decode base64 data
            if file_data.startswith('data:'):
                # Handle data URLs (e.g., "data:image/jpeg;base64,/9j/4AAQ...")
                header, encoded = file_data.split(',', 1)
                file_data = encoded

            file_bytes = base64.b64decode(file_data)

            # Generate unique file key
            file_extension = os.path.splitext(
                file_name)[1] if '.' in file_name else ''
            unique_id = str(uuid.uuid4())
            file_key = f"receipts/{user_id}/{unique_id}{file_extension}"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_bytes,
                ContentType=self._get_content_type(file_extension),
                Metadata={
                    'user_id': user_id,
                    'original_filename': file_name,
                    'upload_date': datetime.utcnow().isoformat()
                }
            )

            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{file_key}"

            logger.info(
                f"File uploaded successfully: {file_key} for user {user_id}")

            return {
                'success': True,
                'file_url': file_url,
                'file_key': file_key,
                'file_name': file_name
            }

        except Exception as e:
            logger.error(
                f"Error uploading file to S3: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, file_key):
        """
        Delete a file from S3.

        Args:
            file_key: S3 key of the file to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"File deleted successfully: {file_key}")
            return True
        except Exception as e:
            logger.error(
                f"Error deleting file from S3: {str(e)}", exc_info=True)
            return False

    def generate_presigned_url(self, file_key, expiration=3600):
        """
        Generate a presigned URL for file access.

        Args:
            file_key: S3 key of the file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(
                f"Error generating presigned URL: {str(e)}", exc_info=True)
            return None

    def _get_content_type(self, file_extension):
        """Get MIME content type based on file extension."""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

    def check_bucket_exists(self):
        """Check if the S3 bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"S3 bucket {self.bucket_name} does not exist")
                return False
            else:
                logger.error(f"Error checking S3 bucket: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking S3 bucket: {str(e)}")
            return False
