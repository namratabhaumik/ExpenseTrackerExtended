"""Unit tests for local implementation classes (auth, expense repo, file storage)."""

import base64
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from ..implementations.local_auth_service import LocalAuthService
from ..implementations.local_file_storage import LocalFileStorage
from ..implementations.sqlite_expense_repo import SQLiteExpenseRepository


class LocalAuthServiceTest(TestCase):
    """Test local authentication service (mock auth for local development)."""

    def setUp(self):
        """Initialize auth service"""
        self.auth_service = LocalAuthService()

    def test_login_success(self):
        """Test successful login with valid credentials"""
        tokens, error = self.auth_service.login('user@example.com', 'password123')

        self.assertIsNone(error)
        self.assertIsNotNone(tokens)
        self.assertIn('id_token', tokens)
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)

    def test_login_returns_valid_tokens(self):
        """Test login returns decodable tokens"""
        tokens, error = self.auth_service.login('test@example.com', 'password')

        for token_name in ['id_token', 'access_token', 'refresh_token']:
            token = tokens[token_name]
            decoded = base64.b64decode(token).decode()
            payload = json.loads(decoded)
            self.assertEqual(payload['sub'], 'test@example.com')

    def test_login_missing_email(self):
        """Test login fails with missing email"""
        tokens, error = self.auth_service.login('', 'password123')

        self.assertIsNone(tokens)
        self.assertIsNotNone(error)
        self.assertIn('Missing', error)

    def test_login_missing_password(self):
        """Test login fails with missing password"""
        tokens, error = self.auth_service.login('user@example.com', '')

        self.assertIsNone(tokens)
        self.assertIsNotNone(error)
        self.assertIn('Missing', error)

    def test_login_none_credentials(self):
        """Test login fails with None credentials"""
        tokens, error = self.auth_service.login(None, None)

        self.assertIsNone(tokens)
        self.assertIsNotNone(error)

    def test_signup_success(self):
        """Test successful signup with valid email"""
        success, error = self.auth_service.signup('newuser@example.com', 'password123')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_signup_auto_confirms(self):
        """Test signup returns success immediately (auto-confirm in local mode)"""
        success, error = self.auth_service.signup('user@example.com', 'password')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_signup_missing_email(self):
        """Test signup fails with missing email"""
        success, error = self.auth_service.signup('', 'password123')

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_signup_missing_password(self):
        """Test signup fails with missing password"""
        success, error = self.auth_service.signup('user@example.com', '')

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_signup_invalid_email(self):
        """Test signup fails with invalid email (no @)"""
        success, error = self.auth_service.signup('invalidemail', 'password123')

        self.assertFalse(success)
        self.assertIn('Invalid email', error)

    def test_confirm_signup(self):
        """Test confirm signup (placeholder for local mode)"""
        success, error = self.auth_service.confirm_signup('user@example.com', '123456')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_forgot_password(self):
        """Test forgot password (placeholder for local mode)"""
        success, error = self.auth_service.forgot_password('user@example.com')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_confirm_forgot_password(self):
        """Test confirm forgot password (placeholder for local mode)"""
        success, error = self.auth_service.confirm_forgot_password(
            'user@example.com', '123456', 'NewPassword123!'
        )

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_verify_reset_code(self):
        """Test verify reset code (placeholder for local mode)"""
        success, error = self.auth_service.verify_reset_code('user@example.com', '123456')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_change_password(self):
        """Test change password (always succeeds in local mode)"""
        success, error = self.auth_service.change_password(
            'user1', 'oldpass', 'newpass123'
        )

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_get_user_profile(self):
        """Test get user profile (placeholder for local mode)"""
        profile, error = self.auth_service.get_user_profile('user123')

        self.assertIsNotNone(profile)
        self.assertIsNone(error)
        self.assertEqual(profile['user_id'], 'user123')

    def test_update_user_profile(self):
        """Test update user profile (placeholder for local mode)"""
        profile, error = self.auth_service.update_user_profile(
            'user123', name='John Doe'
        )

        self.assertIsNotNone(profile)
        self.assertIsNone(error)


class SQLiteExpenseRepositoryTest(TestCase):
    """Test SQLite expense repository implementation."""

    def setUp(self):
        """Create test user and repository"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.repo = SQLiteExpenseRepository()

    def test_create_expense(self):
        """Test creating an expense"""
        result = self.repo.create(
            user_id=self.user.id,
            amount=25.50,
            category='Food',
            description='Lunch'
        )

        self.assertIn('expense_id', result)
        self.assertEqual(result['amount'], 25.50)
        self.assertEqual(result['category'], 'Food')

    def test_create_expense_defaults(self):
        """Test creating expense with default description"""
        result = self.repo.create(
            user_id=self.user.id,
            amount=15.00,
            category='Transport'
        )

        self.assertEqual(result['description'], '')
        self.assertIsNone(result['receipt_url'])

    def test_get_by_user(self):
        """Test retrieving expenses by user"""
        self.repo.create(self.user.id, 10.00, 'Food')
        self.repo.create(self.user.id, 20.00, 'Transport')

        expenses = self.repo.get_by_user(self.user.id)

        self.assertEqual(len(expenses), 2)
        amounts = [e['amount'] for e in expenses]
        self.assertIn(10.00, amounts)
        self.assertIn(20.00, amounts)

    def test_get_by_user_empty(self):
        """Test getting expenses for user with no expenses"""
        expenses = self.repo.get_by_user(self.user.id)

        self.assertEqual(len(expenses), 0)

    def test_get_by_id(self):
        """Test retrieving specific expense"""
        created = self.repo.create(self.user.id, 30.00, 'Entertainment')
        expense_id = created['expense_id']

        result = self.repo.get_by_id(expense_id)

        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 30.00)

    def test_get_by_id_not_found(self):
        """Test retrieving non-existent expense"""
        result = self.repo.get_by_id(99999)

        self.assertIsNone(result)

    def test_update_receipt_url(self):
        """Test updating receipt URL"""
        created = self.repo.create(self.user.id, 25.00, 'Travel')
        expense_id = created['expense_id']

        success = self.repo.update_receipt_url(expense_id, 'https://example.com/receipt.jpg')

        self.assertTrue(success)
        updated = self.repo.get_by_id(expense_id)
        self.assertEqual(updated['receipt_url'], 'https://example.com/receipt.jpg')

    def test_update_receipt_url_not_found(self):
        """Test updating receipt URL for non-existent expense"""
        success = self.repo.update_receipt_url(99999, 'https://example.com/receipt.jpg')

        self.assertFalse(success)

    def test_add_expense_with_receipt(self):
        """Test creating expense with receipt URL"""
        result = self.repo.add_expense_with_receipt(
            user_id=self.user.id,
            amount=40.00,
            category='Dining',
            description='Dinner',
            receipt_url='https://example.com/receipt.jpg'
        )

        self.assertEqual(result['receipt_url'], 'https://example.com/receipt.jpg')
        self.assertEqual(result['amount'], 40.00)

    def test_user_isolation(self):
        """Test expenses are isolated by user"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

        self.repo.create(self.user.id, 10.00, 'Food')
        self.repo.create(other_user.id, 20.00, 'Transport')

        user1_expenses = self.repo.get_by_user(self.user.id)
        user2_expenses = self.repo.get_by_user(other_user.id)

        self.assertEqual(len(user1_expenses), 1)
        self.assertEqual(len(user2_expenses), 1)

    def test_expenses_ordered_by_timestamp(self):
        """Test expenses are returned in reverse chronological order"""
        exp1 = self.repo.create(self.user.id, 10.00, 'Food')
        exp2 = self.repo.create(self.user.id, 20.00, 'Transport')

        expenses = self.repo.get_by_user(self.user.id)

        # Most recent should be first
        self.assertEqual(expenses[0]['expense_id'], exp2['expense_id'])
        self.assertEqual(expenses[1]['expense_id'], exp1['expense_id'])


class LocalFileStorageTest(TestCase):
    """Test local file storage implementation (mock storage for local development)."""

    def setUp(self):
        """Initialize storage"""
        self.storage = LocalFileStorage()

    def test_upload_returns_mock_url(self):
        """Test upload returns mock URL"""
        file_data = b'test file content'
        result = self.storage.upload('test.txt', file_data, user_id=1)

        self.assertIsNotNone(result)
        self.assertIn('mock-files', result)
        self.assertIn('localhost:8000', result)

    def test_upload_includes_user_id(self):
        """Test upload URL includes user ID"""
        result = self.storage.upload('file.txt', b'content', user_id=123)

        self.assertIn('123', result)

    def test_upload_generates_unique_urls(self):
        """Test different uploads generate different URLs"""
        url1 = self.storage.upload('file1.txt', b'content1', user_id=1)
        url2 = self.storage.upload('file2.txt', b'content2', user_id=1)

        self.assertNotEqual(url1, url2)

    def test_get_url(self):
        """Test getting mock file URL"""
        url = self.storage.get_url('1/document.pdf')

        self.assertIsNotNone(url)
        self.assertIn('mock-files', url)
        self.assertIn('1/document.pdf', url)
        self.assertIn('localhost:8000', url)

    def test_upload_different_file_types(self):
        """Test uploading different file types"""
        files = [
            ('image.jpg', b'\xff\xd8\xff\xe0'),  # JPEG magic bytes
            ('document.pdf', b'%PDF-1.4'),
            ('text.txt', b'plain text content'),
        ]

        for filename, content in files:
            result = self.storage.upload(filename, content, user_id=1)
            self.assertIsNotNone(result)
            self.assertIn('mock-files', result)

    def test_upload_large_file(self):
        """Test uploading large file (returns URL immediately)"""
        large_data = b'x' * (10 * 1024 * 1024)  # 10MB
        result = self.storage.upload('large.bin', large_data, user_id=1)

        self.assertIsNotNone(result)
        self.assertIn('mock-files', result)

    def test_multiple_users_isolated(self):
        """Test different users get different URL paths"""
        url1 = self.storage.upload('file.txt', b'data', user_id=1)
        url2 = self.storage.upload('file.txt', b'data', user_id=2)

        self.assertIn('1', url1)
        self.assertIn('2', url2)
        self.assertNotEqual(url1, url2)
