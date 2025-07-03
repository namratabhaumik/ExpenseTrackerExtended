import json
import base64
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
import boto3
from moto import mock_aws
import os


class AuthAppTestCase(TestCase):
    """Base test case for auth app tests."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        # Mock environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            'DJANGO_SECRET_KEY': 'test-secret-key',
            'COGNITO_CLIENT_ID': 'testclientid123',
            'COGNITO_CLIENT_SECRET': 'test-client-secret',
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'AWS_REGION': 'us-east-1',
            'DYNAMODB_TABLE_NAME': 'test-expenses-table',
            'S3_BUCKET_NAME': 'test-bucket',
            'S3_REGION': 'us-east-1'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()


class LoginViewTest(AuthAppTestCase):
    """Test cases for login endpoint."""

    @patch('auth_app.views.cognito_client')
    def test_login_success(self, mock_cognito_client):
        """Test successful login with valid credentials."""
        # Mock Cognito response
        mock_cognito_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token',
                'RefreshToken': 'test-refresh-token'
            }
        }

        response = self.client.post(
            reverse('login'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('access_token', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.cognito_client')
    def test_login_invalid_credentials(self, mock_cognito_client):
        """Test login with invalid credentials."""
        # Mock Cognito error response
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'NotAuthorizedException', 'Message': 'Invalid credentials'}}
        mock_cognito_client.initiate_auth.side_effect = ClientError(
            error_response, 'InitiateAuth')

        response = self.client.post(
            reverse('login'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    def test_login_missing_data(self):
        """Test login with missing required fields."""
        response = self.client.post(
            reverse('login'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


class ExpenseViewTest(AuthAppTestCase):
    """Test cases for expense endpoints."""

    def setUp(self):
        """Set up test data for expense tests."""
        super().setUp()
        self.test_expense_data = {
            'amount': 25.50,
            'category': 'Food',
            'description': 'Lunch expense'
        }
        self.test_token = 'test-access-token'

    @mock_aws
    @patch('auth_app.middleware.boto3.client')
    @patch('auth_app.models.settings.DYNAMODB_TABLE_NAME', 'test-expenses-table')
    def test_add_expense_success(self, mock_boto3_client):
        """Test successful expense addition."""
        # Mock Cognito user validation
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        # Set up DynamoDB with correct table name
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-expenses-table',
            KeySchema=[
                {'AttributeName': 'expense_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'expense_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()

        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps(self.test_expense_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('expense_id', data)

    def test_add_expense_invalid_token(self):
        """Test expense addition with invalid token."""
        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps(self.test_expense_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.middleware.boto3.client')
    def test_add_expense_missing_data(self, mock_boto3_client):
        """Test expense addition with missing required fields."""
        # Mock Cognito user validation
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'amount': 25.50}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @mock_aws
    @patch('auth_app.middleware.boto3.client')
    @patch('auth_app.models.settings.DYNAMODB_TABLE_NAME', 'test-expenses-table')
    def test_get_expenses_success(self, mock_boto3_client):
        """Test successful expense retrieval."""
        # Mock Cognito user validation
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        # Set up DynamoDB with correct table name
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-expenses-table',
            KeySchema=[
                {'AttributeName': 'expense_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'expense_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()

        response = self.client.get(
            reverse('get_expenses'),
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('expenses', data)


class ReceiptUploadTest(AuthAppTestCase):
    """Test cases for receipt upload endpoint."""

    def setUp(self):
        """Set up test data for receipt tests."""
        super().setUp()
        self.test_token = 'test-access-token'
        self.test_file_data = {
            'file': base64.b64encode(b'Test receipt content').decode('utf-8'),
            'filename': 'test_receipt.txt'
        }

    @mock_aws
    @patch('auth_app.middleware.boto3.client')
    def test_upload_receipt_success(self, mock_boto3_client):
        """Test successful receipt upload."""
        # Mock Cognito user validation
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        # Set up S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps(self.test_file_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('file_url', data)

    def test_upload_receipt_invalid_token(self):
        """Test receipt upload with invalid token."""
        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps(self.test_file_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.middleware.boto3.client')
    def test_upload_receipt_missing_data(self, mock_boto3_client):
        """Test receipt upload with missing required fields."""
        # Mock Cognito user validation
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({'filename': 'test.txt'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')
