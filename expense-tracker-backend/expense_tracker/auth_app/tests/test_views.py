"""Unit tests for API views using Django's session-based authentication."""

import json
import base64
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class AuthEndpointsTest(TestCase):
    """Test authentication endpoints with session-based auth."""

    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'Test_Pass_1!'

    def test_login_success(self):
        """Test successful login"""
        # Create a user first
        User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )

        response = self.client.post(
            reverse('login'),
            data=json.dumps({'email': self.test_email, 'password': self.test_password}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['email'], self.test_email)
        self.assertIn('csrf_token', data)
        # Check that session cookie is set
        self.assertIn('sessionid', self.client.cookies)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Create a user
        User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )

        response = self.client.post(
            reverse('login'),
            data=json.dumps({'email': self.test_email, 'password': 'wrong_password'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.client.post(
            reverse('login'),
            data=json.dumps({'email': self.test_email}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_signup_success(self):
        """Test successful signup"""
        response = self.client.post(
            reverse('signup'),
            data=json.dumps({'email': 'newuser@example.com', 'password': self.test_password}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['email'], 'newuser@example.com')
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())

    def test_signup_user_already_exists(self):
        """Test signup when user already exists"""
        User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )

        response = self.client.post(
            reverse('signup'),
            data=json.dumps({'email': self.test_email, 'password': self.test_password}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertIn('error', data)

    def test_confirm_signup_success(self):
        """Test successful signup confirmation (placeholder endpoint)"""
        response = self.client.post(
            reverse('confirm_signup'),
            data=json.dumps({'email': 'user@example.com', 'code': '123456'}),
            content_type='application/json',
        )

        # This is a placeholder endpoint that returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

    def test_forgot_password(self):
        """Test forgot password request (placeholder endpoint)"""
        response = self.client.post(
            reverse('forgot_password'),
            data=json.dumps({'email': 'user@example.com'}),
            content_type='application/json',
        )

        # This is a placeholder endpoint that returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

    def test_confirm_forgot_password(self):
        """Test password reset confirmation (placeholder endpoint)"""
        response = self.client.post(
            reverse('confirm_forgot_password'),
            data=json.dumps({
                'email': 'user@example.com',
                'code': '123456',
                'new_password': self.test_password,
            }),
            content_type='application/json',
        )

        # This is a placeholder endpoint that returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

    def test_verify_reset_code(self):
        """Test reset code verification (placeholder endpoint)"""
        response = self.client.post(
            reverse('verify_reset_code'),
            data=json.dumps({'email': 'user@example.com', 'code': '123456'}),
            content_type='application/json',
        )

        # This is a placeholder endpoint that returns 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)


class CSRFTokenEndpointTest(TestCase):
    """Test CSRF token endpoint."""

    def setUp(self):
        self.client = Client()

    def test_csrf_token_generation(self):
        """Test CSRF token is generated and returned"""
        response = self.client.get(reverse('csrf_token'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('csrf_token', data)
        self.assertTrue(len(data['csrf_token']) > 0)


class LogoutEndpointTest(TestCase):
    """Test logout endpoint."""

    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'Test_Pass_1!'
        self.user = User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )

    def test_logout_success(self):
        """Test successful logout"""
        # Login first
        self.client.login(username=self.test_email, password=self.test_password)

        # Then logout
        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)


class ExpenseEndpointsTest(TestCase):
    """Test expense endpoints with session auth."""

    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'Test_Pass_1!'
        self.user = User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )
        # Login
        self.client.login(username=self.test_email, password=self.test_password)

    @patch('auth_app.views.get_expense_repository')
    def test_add_expense_success(self, mock_get_repo):
        """Test adding expense with authentication"""
        mock_repo = Mock()
        mock_repo.create.return_value = {
            'expense_id': 'test-id',
            'amount': 50.0,
            'category': 'Food',
            'description': 'Test expense'
        }
        mock_get_repo.return_value = mock_repo

        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'amount': 50.0, 'category': 'Food', 'description': 'Test expense'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('expense_id', data)

    def test_add_expense_missing_fields(self):
        """Test adding expense with missing required fields"""
        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'amount': 50.0}),  # Missing category
            content_type='application/json',
        )

        # Request succeeds auth but fails validation
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_add_expense_not_authenticated(self):
        """Test adding expense without authentication"""
        self.client.logout()

        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'amount': 50.0, 'category': 'Food'}),
            content_type='application/json',
        )

        # Should redirect to login
        self.assertIn(response.status_code, [301, 302])

    @patch('auth_app.views.get_expense_repository')
    def test_get_expenses_success(self, mock_get_repo):
        """Test retrieving expenses list"""
        mock_repo = Mock()
        mock_repo.get_by_user.return_value = [
            {'expense_id': 'test-1', 'amount': 25.50, 'category': 'Food'},
            {'expense_id': 'test-2', 'amount': 15.00, 'category': 'Transport'}
        ]
        mock_get_repo.return_value = mock_repo

        response = self.client.get(reverse('get_expenses'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('expenses', data)
        self.assertEqual(len(data['expenses']), 2)

    def test_get_expenses_not_authenticated(self):
        """Test retrieving expenses without authentication"""
        self.client.logout()

        response = self.client.get(reverse('get_expenses'))

        # Should redirect to login
        self.assertIn(response.status_code, [301, 302])


class ReceiptUploadEndpointTest(TestCase):
    """Test receipt upload endpoint."""

    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'Test_Pass_1!'
        self.user = User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password
        )
        # Login
        self.client.login(username=self.test_email, password=self.test_password)

    @patch('auth_app.views.get_file_storage')
    def test_upload_receipt_success(self, mock_get_storage):
        """Test successful receipt upload"""
        mock_storage = Mock()
        mock_storage.upload.return_value = 'https://example.com/receipt.jpg'
        mock_get_storage.return_value = mock_storage

        file_data = base64.b64encode(b'test file content').decode('utf-8')
        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({
                'file': file_data,
                'filename': 'test_receipt.jpg',
                'expense_id': 'test-expense-1'
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('file_url', data)
        self.assertIn('file_name', data)

    def test_upload_receipt_missing_file(self):
        """Test receipt upload with missing file"""
        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({'filename': 'test.jpg'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_upload_receipt_missing_filename(self):
        """Test receipt upload with missing filename"""
        file_data = base64.b64encode(b'test').decode('utf-8')
        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({'file': file_data}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_upload_receipt_not_authenticated(self):
        """Test receipt upload without authentication"""
        self.client.logout()

        file_data = base64.b64encode(b'test').decode('utf-8')
        response = self.client.post(
            reverse('upload_receipt'),
            data=json.dumps({'file': file_data, 'filename': 'test.jpg'}),
            content_type='application/json',
        )

        # Should redirect to login
        self.assertIn(response.status_code, [301, 302])


class ProfileEndpointsTest(TestCase):
    """Test profile endpoints."""

    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'Test_Pass_1!'
        self.user = User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password,
            first_name='Test User'
        )
        # Login
        self.client.login(username=self.test_email, password=self.test_password)

    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['email'], self.test_email)

    def test_update_profile(self):
        """Test updating user profile"""
        response = self.client.put(
            reverse('profile'),
            data=json.dumps({'name': 'Updated Name'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

        # Verify update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated Name')

    def test_change_password_success(self):
        """Test successful password change"""
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps({
                'current_password': self.test_password,
                'new_password': 'Test_New_1!',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

        # User should be logged out after password change
        profile_response = self.client.get(reverse('profile'))
        self.assertIn(profile_response.status_code, [301, 302])

    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps({
                'current_password': 'WrongPassword123!',
                'new_password': 'Test_New_1!',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)

    def test_change_password_missing_fields(self):
        """Test password change with missing fields"""
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps({'current_password': self.test_password}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_profile_not_authenticated(self):
        """Test profile access without authentication"""
        self.client.logout()

        response = self.client.get(reverse('profile'))

        # Should redirect to login
        self.assertIn(response.status_code, [301, 302])


class MethodValidationTest(TestCase):
    """Test HTTP method validation on endpoints."""

    def setUp(self):
        self.client = Client()

    def test_login_rejects_get(self):
        """Login endpoint requires POST"""
        response = self.client.get(reverse('login'))
        # Signup is @csrf_exempt POST only
        self.assertIn(response.status_code, [401, 405])

    def test_login_rejects_put(self):
        """Login endpoint requires POST"""
        response = self.client.put(
            reverse('login'),
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json',
        )
        self.assertIn(response.status_code, [401, 405])

    def test_signup_rejects_delete(self):
        """Signup endpoint requires POST"""
        response = self.client.delete(reverse('signup'))
        # Signup is @csrf_exempt POST only
        self.assertIn(response.status_code, [401, 405])


class ErrorHandlingTest(TestCase):
    """Test error handling in views."""

    def setUp(self):
        self.client = Client()

    def test_invalid_json_in_login(self):
        """Login handles invalid JSON"""
        response = self.client.post(
            reverse('login'),
            data='invalid json {',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_invalid_json_in_signup(self):
        """Signup handles invalid JSON"""
        response = self.client.post(
            reverse('signup'),
            data='not valid json [',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
