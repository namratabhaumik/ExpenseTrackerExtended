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

    @patch('auth_app.views.get_cognito_client')
    def test_login_success(self, mock_get_cognito_client):
        """Test successful login with valid credentials."""
        # Mock Cognito client and response
        mock_cognito_client = MagicMock()
        mock_cognito_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token',
                'RefreshToken': 'test-refresh-token'
            }
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('login'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Check that access_token is set as a cookie, not in the JSON body
        self.assertIn('access_token', response.cookies)
        cookie = response.cookies['access_token']
        self.assertTrue(cookie.value)
        self.assertTrue(cookie['httponly'])
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.get_cognito_client')
    def test_login_invalid_credentials(self, mock_get_cognito_client):
        """Test login with invalid credentials."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'NotAuthorizedException', 'Message': 'Invalid credentials'}}
        mock_cognito_client.initiate_auth.side_effect = ClientError(
            error_response, 'InitiateAuth')
        mock_get_cognito_client.return_value = mock_cognito_client

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
    @patch('auth_app.middleware.get_cognito_client')
    @patch('auth_app.models.get_dynamodb_table')
    def test_add_expense_success(self, mock_get_dynamodb_table, mock_get_cognito_client):
        """Test successful expense addition."""
        # Mock Cognito user validation
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_table.put_item.return_value = None
        mock_get_dynamodb_table.return_value = mock_table

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

    @patch('auth_app.middleware.get_cognito_client')
    def test_add_expense_missing_data(self, mock_get_cognito_client):
        """Test expense addition with missing required fields."""
        # Mock Cognito user validation
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_get_cognito_client.return_value = mock_cognito_client

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
    @patch('auth_app.middleware.get_cognito_client')
    @patch('auth_app.models.get_dynamodb_table')
    def test_get_expenses_success(self, mock_get_dynamodb_table, mock_get_cognito_client):
        """Test successful expense retrieval."""
        # Mock Cognito user validation
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            'Items': [
                {
                    'expense_id': 'test-expense-1',
                    'user_id': 'test-user-id',
                    'amount': 25.50,
                    'category': 'Food',
                    'description': 'Lunch',
                    'timestamp': '2024-01-01T00:00:00'
                }
            ]
        }
        mock_get_dynamodb_table.return_value = mock_table

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
        """Set up test data for receipt upload tests."""
        super().setUp()
        self.test_file_data = {
            'file': base64.b64encode(b'Test file content').decode('utf-8'),
            'filename': 'test_receipt.jpg',
            'expense_id': 'test-expense-1'
        }
        self.test_token = 'test-access-token'

    @mock_aws
    @patch('auth_app.middleware.get_cognito_client')
    @patch('utils.s3_utils.get_s3_client')
    def test_upload_receipt_success(self, mock_get_s3_client, mock_get_cognito_client):
        """Test successful receipt upload."""
        # Mock Cognito user validation
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_s3_client.put_object.return_value = None
        mock_s3_client.head_bucket.return_value = None
        mock_get_s3_client.return_value = mock_s3_client

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

    @patch('auth_app.middleware.get_cognito_client')
    def test_upload_receipt_missing_data(self, mock_get_cognito_client):
        """Test receipt upload with missing required fields."""
        # Mock Cognito user validation
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({'file': 'test-data'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.test_token}'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


class SignupViewTest(AuthAppTestCase):
    """Test cases for signup endpoint."""

    @patch('auth_app.views.get_cognito_client')
    def test_signup_success(self, mock_get_cognito_client):
        """Test successful signup."""
        # Mock Cognito client and response
        mock_cognito_client = MagicMock()
        mock_cognito_client.sign_up.return_value = {
            'UserSub': 'test-user-sub'
        }
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('signup'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.get_cognito_client')
    def test_signup_user_exists(self, mock_get_cognito_client):
        """Test signup with existing user."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'UsernameExistsException', 'Message': 'User already exists'}}
        mock_cognito_client.sign_up.side_effect = ClientError(
            error_response, 'SignUp')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('signup'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.views.get_cognito_client')
    def test_signup_invalid_password(self, mock_get_cognito_client):
        """Test signup with invalid password."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'InvalidPasswordException', 'Message': 'Invalid password'}}
        mock_cognito_client.sign_up.side_effect = ClientError(
            error_response, 'SignUp')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('signup'),
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


class ConfirmSignupViewTest(AuthAppTestCase):
    """Test cases for confirm signup endpoint."""

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_signup_success(self, mock_get_cognito_client):
        """Test successful signup confirmation."""
        # Mock Cognito client
        mock_cognito_client = MagicMock()
        mock_cognito_client.confirm_sign_up.return_value = None
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_signup'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_signup_invalid_code(self, mock_get_cognito_client):
        """Test signup confirmation with invalid code."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'CodeMismatchException', 'Message': 'Invalid code'}}
        mock_cognito_client.confirm_sign_up.side_effect = ClientError(
            error_response, 'ConfirmSignUp')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_signup'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_signup_already_confirmed(self, mock_get_cognito_client):
        """Test signup confirmation for already confirmed user."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'NotAuthorizedException', 'Message': 'Already confirmed'}}
        mock_cognito_client.confirm_sign_up.side_effect = ClientError(
            error_response, 'ConfirmSignUp')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_signup'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


class ForgotPasswordViewTest(AuthAppTestCase):
    """Test cases for forgot password endpoint."""

    @patch('auth_app.views.get_cognito_client')
    def test_forgot_password_success(self, mock_get_cognito_client):
        """Test successful forgot password request."""
        # Mock Cognito client
        mock_cognito_client = MagicMock()
        mock_cognito_client.forgot_password.return_value = None
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('forgot_password'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.get_cognito_client')
    def test_forgot_password_user_not_found(self, mock_get_cognito_client):
        """Test forgot password with non-existent user."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'UserNotFoundException', 'Message': 'User not found'}}
        mock_cognito_client.forgot_password.side_effect = ClientError(
            error_response, 'ForgotPassword')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('forgot_password'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.views.get_cognito_client')
    def test_forgot_password_limit_exceeded(self, mock_get_cognito_client):
        """Test forgot password with limit exceeded."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'LimitExceededException', 'Message': 'Limit exceeded'}}
        mock_cognito_client.forgot_password.side_effect = ClientError(
            error_response, 'ForgotPassword')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('forgot_password'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 429)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    def test_forgot_password_missing_email(self):
        """Test forgot password with missing email."""
        response = self.client.post(
            reverse('forgot_password'),
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


class ConfirmForgotPasswordViewTest(AuthAppTestCase):
    """Test cases for confirm forgot password endpoint."""

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_forgot_password_success(self, mock_get_cognito_client):
        """Test successful password reset confirmation."""
        # Mock Cognito client
        mock_cognito_client = MagicMock()
        mock_cognito_client.confirm_forgot_password.return_value = None
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456',
                'new_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_forgot_password_invalid_code(self, mock_get_cognito_client):
        """Test password reset confirmation with invalid code."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'CodeMismatchException', 'Message': 'Invalid code'}}
        mock_cognito_client.confirm_forgot_password.side_effect = ClientError(
            error_response, 'ConfirmForgotPassword')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456',
                'new_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_forgot_password_expired_code(self, mock_get_cognito_client):
        """Test password reset confirmation with expired code."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'ExpiredCodeException', 'Message': 'Code expired'}}
        mock_cognito_client.confirm_forgot_password.side_effect = ClientError(
            error_response, 'ConfirmForgotPassword')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456',
                'new_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    @patch('auth_app.views.get_cognito_client')
    def test_confirm_forgot_password_invalid_password(self, mock_get_cognito_client):
        """Test password reset confirmation with invalid password."""
        # Mock Cognito client and error response
        mock_cognito_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {'Code': 'InvalidPasswordException', 'Message': 'Invalid password'}}
        mock_cognito_client.confirm_forgot_password.side_effect = ClientError(
            error_response, 'ConfirmForgotPassword')
        mock_get_cognito_client.return_value = mock_cognito_client

        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({
                'email': 'test@example.com',
                'code': '123456',
                'new_password': 'weak'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    def test_confirm_forgot_password_missing_fields(self):
        """Test password reset confirmation with missing fields."""
        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')


@patch('auth_app.middleware.get_cognito_client')
@patch('auth_app.views.get_cognito_client')
class ProfileViewTest(AuthAppTestCase):
    """Test cases for profile management endpoints."""

    def test_get_profile_success(self, mock_views_cognito, mock_middleware_cognito):
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }
        mock_views_cognito.return_value = mock_cognito_client
        mock_middleware_cognito.return_value = mock_cognito_client
        self.client.cookies['access_token'] = 'fake-test-token'
        response = self.client.get(
            reverse('profile')
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['email'], 'test@example.com')
        self.assertEqual(data['profile']['name'], 'Test User')

    def test_update_profile_success(self, mock_views_cognito, mock_middleware_cognito):
        mock_cognito_client = MagicMock()
        mock_cognito_client.update_user_attributes.return_value = {}
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }
        mock_views_cognito.return_value = mock_cognito_client
        mock_middleware_cognito.return_value = mock_cognito_client
        self.client.cookies['access_token'] = 'fake-test-token'
        response = self.client.put(
            reverse('profile'),
            data=json.dumps({'email': 'new@example.com', 'name': 'New Name'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    def test_change_password_success(self, mock_views_cognito, mock_middleware_cognito):
        mock_cognito_client = MagicMock()
        mock_cognito_client.change_password.return_value = {}
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }
        mock_views_cognito.return_value = mock_cognito_client
        mock_middleware_cognito.return_value = mock_cognito_client
        self.client.cookies['access_token'] = 'fake-test-token'
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps({'current_password': 'oldPass123!',
                            'new_password': 'newPass456!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')

    def test_update_profile_no_fields(self, mock_views_cognito, mock_middleware_cognito):
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }
        mock_views_cognito.return_value = mock_cognito_client
        mock_middleware_cognito.return_value = mock_cognito_client
        self.client.cookies['access_token'] = 'fake-test-token'
        response = self.client.put(
            reverse('profile'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')

    def test_change_password_missing_fields(self, mock_views_cognito, mock_middleware_cognito):
        mock_cognito_client = MagicMock()
        mock_cognito_client.get_user.return_value = {
            'Username': 'test-user-id',
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }
        mock_views_cognito.return_value = mock_cognito_client
        mock_middleware_cognito.return_value = mock_cognito_client
        self.client.cookies['access_token'] = 'fake-test-token'
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps({'current_password': 'oldPass123!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'error')
