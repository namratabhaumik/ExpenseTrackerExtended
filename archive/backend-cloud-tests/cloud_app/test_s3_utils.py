import base64
import os

# Import the S3Utils class
import sys
from unittest.mock import MagicMock, patch

import boto3
from django.test import TestCase, override_settings
from moto import mock_aws

from .s3_utils import S3Handler

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class S3UtilsTestCase(TestCase):
    """Test cases for S3Utils class."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.override = override_settings(
            AWS_ACCESS_KEY_ID='test-access-key',
            AWS_SECRET_ACCESS_KEY='test-secret-key',
            AWS_REGION='us-east-1',
            S3_BUCKET_NAME='test-bucket',
            S3_REGION='us-east-1'
        )
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        super().tearDownClass()

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'AWS_REGION': 'us-east-1',
            'S3_BUCKET_NAME': 'test-bucket',
            'S3_REGION': 'us-east-1'
        })
        self.env_patcher.start()

        self.s3_utils = S3Handler()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    def test_upload_file_success(self):
        """Test successful file upload to S3."""
        with mock_aws():
            # Set up S3
            s3 = boto3.client('s3', region_name='us-east-1')
            s3.create_bucket(Bucket='test-bucket')

            # Create a test file (base64-encoded string)
            test_content = base64.b64encode(
                b'Test file content').decode('utf-8')
            test_filename = 'test_file.txt'
            test_user_id = 'test-user'

            # Test upload
            result = self.s3_utils.upload_file(
                test_content, test_filename, test_user_id)

            self.assertIsNotNone(result)
            self.assertIn('file_url', result)
            self.assertIn('file_key', result)
            self.assertTrue(result['success'])

    def test_upload_file_with_custom_path(self):
        """Test file upload with custom user_id."""
        with mock_aws():
            # Set up S3
            s3 = boto3.client('s3', region_name='us-east-1')
            s3.create_bucket(Bucket='test-bucket')

            # Create a test file (base64-encoded string)
            test_content = base64.b64encode(
                b'Test file content').decode('utf-8')
            test_filename = 'test_file.txt'
            test_user_id = 'receipts-2024-01-user'

            # Test upload
            result = self.s3_utils.upload_file(
                test_content, test_filename, test_user_id)

            self.assertIsNotNone(result)
            self.assertIn('file_url', result)
            self.assertIn('file_key', result)
            self.assertTrue(result['success'])
            self.assertIn(test_user_id, result['file_key'])

    def test_upload_file_s3_error(self):
        """Test file upload with S3 error."""
        with mock_aws():
            # Don't create bucket to simulate S3 error
            test_content = base64.b64encode(
                b'Test file content').decode('utf-8')
            test_filename = 'test_file.txt'
            test_user_id = 'test-user'

            # Test upload
            result = self.s3_utils.upload_file(
                test_content, test_filename, test_user_id)

            self.assertIsNotNone(result)
            self.assertFalse(result['success'])
            self.assertIn('error', result)

    def test_upload_file_empty_content(self):
        """Test file upload with empty content."""
        test_content = ''
        test_filename = 'test_file.txt'
        test_user_id = 'test-user'

        # Test upload
        result = self.s3_utils.upload_file(
            test_content, test_filename, test_user_id)

        self.assertIsNotNone(result)
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_upload_file_empty_filename(self):
        """Test file upload with empty filename."""
        test_content = base64.b64encode(b'Test content').decode('utf-8')
        test_filename = ''
        test_user_id = 'test-user'

        # Test upload
        result = self.s3_utils.upload_file(
            test_content, test_filename, test_user_id)

        self.assertIsNotNone(result)
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_delete_file_success(self):
        """Test successful file deletion from S3."""
        with mock_aws():
            # Set up S3
            s3 = boto3.client('s3', region_name='us-east-1')
            s3.create_bucket(Bucket='test-bucket')

            # Upload a file first
            test_content = base64.b64encode(
                b'Test file content').decode('utf-8')
            test_filename = 'test_file.txt'
            test_user_id = 'test-user'
            upload_result = self.s3_utils.upload_file(
                test_content, test_filename, test_user_id)

            # Test deletion
            file_key = upload_result['file_key']
            result = self.s3_utils.delete_file(file_key)

            self.assertIsInstance(result, bool)
            self.assertTrue(result)

    def test_delete_file_not_found(self):
        """Test file deletion when file doesn't exist."""
        with mock_aws():
            # Set up S3
            s3 = boto3.client('s3', region_name='us-east-1')
            s3.create_bucket(Bucket='test-bucket')

            # Test deletion of non-existent file
            result = self.s3_utils.delete_file('non-existent-file.txt')

            self.assertIsInstance(result, bool)
            # S3 delete_object is idempotent and returns success
            self.assertTrue(result)

    @patch('auth_app.implementations.cloud.utils.s3_utils.get_s3_client')
    def test_s3_client_initialization(self, mock_get_s3_client):
        """Test S3 client initialization."""
        mock_s3_client = MagicMock()
        mock_get_s3_client.return_value = mock_s3_client

        # Create new instance to trigger client initialization
        S3Handler()

        # Verify get_s3_client was called
        mock_get_s3_client.assert_called_once()
