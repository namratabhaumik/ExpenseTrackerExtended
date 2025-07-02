import json
import base64
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
import boto3
from moto import mock_dynamodb, mock_s3
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
            'COGNITO_CLIENT_ID': 'test-client-id',
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

    @patch('auth_app.views.boto3.client')
    def test_login_success(self, mock_boto3_client):
        """Test successful login with valid credentials."""
        # Mock Cognito response
        mock_cognito = MagicMock()
        mock_cognito.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token',
                'RefreshToken': 'test-refresh-token'
            }
        }
        mock_boto3_client.return_value = mock_cognito

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

    @patch('auth_app.views.boto3.client')
    def test_login_invalid_credentials(self, mock_boto3_client):
        """Test login with invalid credentials."""
        # Mock Cognito error response
        mock_cognito = MagicMock()
        mock_cognito.initiate_auth.side_effect = Exception(
            'Invalid credentials')
        mock_boto3_client.return_value = mock_cognito

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

    @mock_dynamodb
    @patch('auth_app.views.verify_cognito_token')
    def test_add_expense_success(self, mock_verify_token):
        """Test successful expense addition."""
        # Mock token verification
        mock_verify_token.return_value = {'sub': 'test-user-id'}

        # Set up DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-expenses-table',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
                {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
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

    @patch('auth_app.views.verify_cognito_token')
    def test_add_expense_invalid_token(self, mock_verify_token):
        """Test expense addition with invalid token."""
        mock_verify_token.side_effect = Exception('Invalid token')

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

    def test_add_expense_missing_data(self):
        """Test expense addition with missing required fields."""
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

    @mock_dynamodb
    @patch('auth_app.views.verify_cognito_token')
    def test_get_expenses_success(self, mock_verify_token):
        """Test successful expense retrieval."""
        # Mock token verification
        mock_verify_token.return_value = {'sub': 'test-user-id'}

        # Set up DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-expenses-table',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
                {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
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

    @mock_s3
    @patch('auth_app.views.verify_cognito_token')
    def test_upload_receipt_success(self, mock_verify_token):
        """Test successful receipt upload."""
        # Mock token verification
        mock_verify_token.return_value = {'sub': 'test-user-id'}

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

    @patch('auth_app.views.verify_cognito_token')
    def test_upload_receipt_invalid_token(self, mock_verify_token):
        """Test receipt upload with invalid token."""
        mock_verify_token.side_effect = Exception('Invalid token')

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

    def test_upload_receipt_missing_data(self):
        """Test receipt upload with missing required fields."""
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


class UtilityFunctionTest(TestCase):
    """Test cases for utility functions."""

    @patch('auth_app.views.boto3.client')
    def test_verify_cognito_token_success(self, mock_boto3_client):
        """Test successful token verification."""
        mock_cognito = MagicMock()
        mock_cognito.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_boto3_client.return_value = mock_cognito

        from auth_app.views import verify_cognito_token
        result = verify_cognito_token('valid-token')

        self.assertEqual(result['sub'], 'test-user-id')

    @patch('auth_app.views.boto3.client')
    def test_verify_cognito_token_invalid(self, mock_boto3_client):
        """Test invalid token verification."""
        mock_cognito = MagicMock()
        mock_cognito.get_user.side_effect = Exception('Invalid token')
        mock_boto3_client.return_value = mock_cognito

        from auth_app.views import verify_cognito_token

        with self.assertRaises(Exception):
            verify_cognito_token('invalid-token')
