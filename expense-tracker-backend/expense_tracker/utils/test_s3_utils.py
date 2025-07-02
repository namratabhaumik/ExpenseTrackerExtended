from utils.s3_utils import S3Utils
import unittest
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_s3
import os
import tempfile
import base64

# Import the S3Utils class
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class S3UtilsTestCase(unittest.TestCase):
    """Test cases for S3Utils class."""

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

        self.s3_utils = S3Utils()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    @mock_s3
    def test_upload_file_success(self):
        """Test successful file upload to S3."""
        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Create a test file
        test_content = b'Test file content'
        test_filename = 'test_file.txt'

        # Test upload
        result = self.s3_utils.upload_file(test_content, test_filename)

        self.assertIsNotNone(result)
        self.assertIn('file_url', result)
        self.assertIn('file_key', result)
        self.assertEqual(result['status'], 'success')

    @mock_s3
    def test_upload_file_with_custom_path(self):
        """Test file upload with custom path."""
        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Create a test file
        test_content = b'Test file content'
        test_filename = 'test_file.txt'
        custom_path = 'receipts/2024/01/'

        # Test upload
        result = self.s3_utils.upload_file(
            test_content, test_filename, custom_path)

        self.assertIsNotNone(result)
        self.assertIn('file_url', result)
        self.assertIn('file_key', result)
        self.assertEqual(result['status'], 'success')
        self.assertIn(custom_path, result['file_key'])

    @mock_s3
    def test_upload_file_s3_error(self):
        """Test file upload with S3 error."""
        # Don't create bucket to simulate S3 error

        test_content = b'Test file content'
        test_filename = 'test_file.txt'

        # Test upload
        result = self.s3_utils.upload_file(test_content, test_filename)

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)

    def test_upload_file_empty_content(self):
        """Test file upload with empty content."""
        test_content = b''
        test_filename = 'test_file.txt'

        # Test upload
        result = self.s3_utils.upload_file(test_content, test_filename)

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)

    def test_upload_file_empty_filename(self):
        """Test file upload with empty filename."""
        test_content = b'Test content'
        test_filename = ''

        # Test upload
        result = self.s3_utils.upload_file(test_content, test_filename)

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)

    @mock_s3
    def test_delete_file_success(self):
        """Test successful file deletion from S3."""
        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Upload a file first
        test_content = b'Test file content'
        test_filename = 'test_file.txt'
        upload_result = self.s3_utils.upload_file(test_content, test_filename)

        # Test deletion
        file_key = upload_result['file_key']
        result = self.s3_utils.delete_file(file_key)

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')

    @mock_s3
    def test_delete_file_not_found(self):
        """Test file deletion when file doesn't exist."""
        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Test deletion of non-existent file
        result = self.s3_utils.delete_file('non-existent-file.txt')

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)

    @mock_s3
    def test_get_file_url_success(self):
        """Test successful file URL generation."""
        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Upload a file first
        test_content = b'Test file content'
        test_filename = 'test_file.txt'
        upload_result = self.s3_utils.upload_file(test_content, test_filename)

        # Test URL generation
        file_key = upload_result['file_key']
        url = self.s3_utils.get_file_url(file_key)

        self.assertIsNotNone(url)
        self.assertIn('test-bucket', url)
        self.assertIn(file_key, url)

    def test_get_file_url_empty_key(self):
        """Test URL generation with empty file key."""
        url = self.s3_utils.get_file_url('')

        self.assertIsNone(url)

    @patch('utils.s3_utils.boto3.client')
    def test_s3_client_initialization(self, mock_boto3_client):
        """Test S3 client initialization."""
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client

        # Create new instance to trigger client initialization
        s3_utils = S3Utils()

        mock_boto3_client.assert_called_with('s3', region_name='us-east-1')


if __name__ == '__main__':
    unittest.main()
