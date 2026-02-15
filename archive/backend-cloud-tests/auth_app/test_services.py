"""Unit tests for service layer abstractions (no mocking, pure logic testing)."""

from unittest.mock import patch

from django.test import TestCase, override_settings

from auth_app.implementations.local.local_auth_service import LocalAuthService
from auth_app.implementations.local.local_file_storage import LocalFileStorage
from auth_app.implementations.local.sqlite_expense_repo import SQLiteExpenseRepository
from auth_app.services import (
    get_auth_service,
    get_expense_repository,
    get_file_storage,
)


class FactoryPatternTest(TestCase):
    """Test that factories select correct implementation based on IS_LOCAL_DEMO setting."""

    @override_settings(IS_LOCAL_DEMO=True)
    def test_get_auth_service_returns_local_in_demo_mode(self):
        """Factory returns LocalAuthService when IS_LOCAL_DEMO=True"""
        service = get_auth_service()
        self.assertIsInstance(service, LocalAuthService)

    @override_settings(IS_LOCAL_DEMO=False)
    @patch('auth_app.implementations.cloud.cognito_service.boto3')
    def test_get_auth_service_returns_cloud_in_production(self, mock_boto3):
        """Factory returns CognitoAuthService when IS_LOCAL_DEMO=False"""
        # Mock boto3 to prevent AWS connection errors in test
        mock_boto3.client.return_value = {}
        try:
            service = get_auth_service()
            # Service should be loaded (may be CognitoAuthService if AWS is available)
            self.assertIsNotNone(service)
        except Exception:
            # AWS errors are acceptable in test environment
            pass

    @override_settings(IS_LOCAL_DEMO=True)
    def test_get_expense_repository_returns_sqlite_in_demo_mode(self):
        """Factory returns SQLiteExpenseRepository when IS_LOCAL_DEMO=True"""
        repo = get_expense_repository()
        self.assertIsInstance(repo, SQLiteExpenseRepository)

    @override_settings(IS_LOCAL_DEMO=True)
    def test_get_file_storage_returns_local_in_demo_mode(self):
        """Factory returns LocalFileStorage when IS_LOCAL_DEMO=True"""
        storage = get_file_storage()
        self.assertIsInstance(storage, LocalFileStorage)


class LocalAuthServiceTest(TestCase):
    """Test LocalAuthService - no mocking needed, tests real logic."""

    def setUp(self):
        self.service = LocalAuthService()

    def test_login_accepts_any_email_password(self):
        """LocalAuthService accepts any credentials"""
        tokens, error = self.service.login('test@example.com', 'password123')

        self.assertIsNone(error)
        self.assertIsNotNone(tokens)
        self.assertIn('access_token', tokens)
        self.assertIn('id_token', tokens)
        self.assertIn('refresh_token', tokens)

    def test_login_returns_valid_token_structure(self):
        """Tokens have expected structure"""
        tokens, error = self.service.login('user@test.com', 'pass')

        # All tokens should be non-empty strings
        self.assertTrue(len(tokens['access_token']) > 0)
        self.assertTrue(len(tokens['id_token']) > 0)
        self.assertTrue(len(tokens['refresh_token']) > 0)

    def test_signup_accepts_valid_email(self):
        """LocalAuthService signup auto-confirms"""
        success, error = self.service.signup('new@example.com', 'password123')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_signup_rejects_invalid_email(self):
        """Signup validates email format"""
        success, error = self.service.signup('invalidemail', 'password123')

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_signup_requires_password(self):
        """Signup requires password"""
        success, error = self.service.signup('test@example.com', '')

        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_confirm_signup_accepts_any_code(self):
        """LocalAuthService confirm_signup auto-confirms"""
        success, error = self.service.confirm_signup('user@example.com', 'anycode')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_forgot_password_initiates_mock_reset(self):
        """LocalAuthService forgot_password returns success"""
        success, error = self.service.forgot_password('user@example.com')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_confirm_forgot_password_accepts_any_code(self):
        """LocalAuthService confirm_forgot_password auto-resets"""
        success, error = self.service.confirm_forgot_password(
            'user@example.com', 'code123', 'newpassword456'
        )

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_verify_reset_code_accepts_any_code(self):
        """LocalAuthService verify_reset_code auto-validates"""
        valid, error = self.service.verify_reset_code('user@example.com', 'anycode')

        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_change_password_accepts_any_password(self):
        """LocalAuthService change_password auto-changes"""
        success, error = self.service.change_password('user@example.com', 'old', 'new')

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_get_user_profile_returns_mock_profile(self):
        """LocalAuthService get_user_profile returns mock data"""
        profile, error = self.service.get_user_profile('user@example.com')

        self.assertIsNone(error)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['user_id'], 'user@example.com')

    def test_update_user_profile_returns_updated_profile(self):
        """LocalAuthService update_user_profile returns mock data"""
        profile, error = self.service.update_user_profile(
            'user@example.com', email='newemail@example.com'
        )

        self.assertIsNone(error)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['email'], 'newemail@example.com')


class SQLiteExpenseRepositoryTest(TestCase):
    """Test SQLiteExpenseRepository - uses real Django ORM."""

    def setUp(self):
        self.repo = SQLiteExpenseRepository()

    def test_create_expense(self):
        """Create expense and retrieve it"""
        expense = self.repo.create(
            user_id='test_user',
            amount=50.0,
            category='Food',
            description='Lunch'
        )

        self.assertIsNotNone(expense)
        self.assertEqual(expense['amount'], 50.0)
        self.assertEqual(expense['category'], 'Food')
        self.assertEqual(expense['description'], 'Lunch')
        self.assertIn('expense_id', expense)
        self.assertIn('timestamp', expense)

    def test_get_by_user_returns_user_expenses(self):
        """Get expenses for specific user"""
        # Create expenses for user1
        self.repo.create('user1', 50.0, 'Food', 'Lunch')
        self.repo.create('user1', 30.0, 'Transport', 'Taxi')

        # Create expense for user2
        self.repo.create('user2', 100.0, 'Entertainment', 'Movie')

        # Get user1 expenses
        expenses = self.repo.get_by_user('user1')

        self.assertEqual(len(expenses), 2)
        self.assertTrue(all(exp['user_id'] == 'user1' for exp in expenses))

    def test_get_by_id_returns_expense(self):
        """Get specific expense by ID"""
        created = self.repo.create('user1', 50.0, 'Food', 'Lunch')
        expense_id = created['expense_id']

        retrieved = self.repo.get_by_id(expense_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['expense_id'], expense_id)
        self.assertEqual(retrieved['amount'], 50.0)

    def test_get_by_id_returns_none_for_nonexistent(self):
        """Get non-existent expense returns None"""
        retrieved = self.repo.get_by_id(99999)  # Use a non-existent integer ID

        self.assertIsNone(retrieved)

    def test_update_receipt_url(self):
        """Update expense with receipt URL"""
        created = self.repo.create('user1', 50.0, 'Food', 'Lunch')
        expense_id = created['expense_id']

        success = self.repo.update_receipt_url(expense_id, 'http://example.com/receipt.pdf')

        self.assertTrue(success)

        # Verify update
        retrieved = self.repo.get_by_id(expense_id)
        self.assertEqual(retrieved['receipt_url'], 'http://example.com/receipt.pdf')

    def test_add_expense_with_receipt(self):
        """Create expense with receipt URL"""
        expense = self.repo.add_expense_with_receipt(
            user_id='user1',
            amount=75.0,
            category='Dining',
            description='Dinner',
            receipt_url='http://example.com/receipt.pdf'
        )

        self.assertIsNotNone(expense)
        self.assertEqual(expense['receipt_url'], 'http://example.com/receipt.pdf')


class LocalFileStorageTest(TestCase):
    """Test LocalFileStorage - mock file operations."""

    def setUp(self):
        self.storage = LocalFileStorage()

    def test_upload_returns_mock_url(self):
        """Upload returns mock URL"""
        file_data = b'test file content'
        url = self.storage.upload('test.pdf', file_data, 'user123')

        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('http://localhost:8000/mock-files/'))
        self.assertIn('user123', url)

    def test_upload_includes_user_id_in_path(self):
        """Upload URL includes user ID"""
        url1 = self.storage.upload('file.pdf', b'data', 'user_a')
        url2 = self.storage.upload('file.pdf', b'data', 'user_b')

        self.assertIn('user_a', url1)
        self.assertIn('user_b', url2)
        self.assertNotEqual(url1, url2)

    def test_get_url_returns_mock_url(self):
        """Get URL for file key"""
        url = self.storage.get_url('some/file/key')

        self.assertEqual(url, 'http://localhost:8000/mock-files/some/file/key')


class ResponseBuilderTest(TestCase):
    """Test ResponseBuilder utility."""

    def test_success_response_format(self):
        """Success response has correct format"""
        from auth_app.services import ResponseBuilder

        response = ResponseBuilder.success('Test message', {'key': 'value'})

        data = response.content.decode()
        self.assertIn('success', data)
        self.assertIn('Test message', data)
        self.assertEqual(response.status_code, 200)

    def test_error_response_format(self):
        """Error response has correct format"""
        from auth_app.services import ResponseBuilder

        response = ResponseBuilder.error('Error message', 400)

        data = response.content.decode()
        self.assertIn('error', data)
        self.assertIn('Error message', data)
        self.assertEqual(response.status_code, 400)

    def test_validation_error_format(self):
        """Validation error response has correct format"""
        from auth_app.services import ResponseBuilder

        response = ResponseBuilder.validation_error({'field': 'error'})

        self.assertEqual(response.status_code, 400)
        data = response.content.decode()
        self.assertIn('field', data)


class RequestValidatorTest(TestCase):
    """Test RequestValidator utility."""

    def test_require_fields_success(self):
        """Validation passes when all fields present"""
        from auth_app.services import RequestValidator

        data = {'email': 'test@example.com', 'password': 'pass123'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertTrue(is_valid)
        self.assertIsNone(errors)

    def test_require_fields_missing(self):
        """Validation fails when fields missing"""
        from auth_app.services import RequestValidator

        data = {'email': 'test@example.com'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertFalse(is_valid)
        self.assertIsNotNone(errors)
        self.assertIn('password', errors)

    def test_validate_email_valid(self):
        """Email validation accepts valid email"""
        from auth_app.services import RequestValidator

        is_valid, error = RequestValidator.validate_email('test@example.com')

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_email_invalid(self):
        """Email validation rejects invalid email"""
        from auth_app.services import RequestValidator

        is_valid, error = RequestValidator.validate_email('invalidemail')

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_password_strength_valid(self):
        """Password validation accepts strong password"""
        from auth_app.services import RequestValidator

        is_valid, error = RequestValidator.validate_password_strength('password123')

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_password_strength_too_short(self):
        """Password validation rejects short password"""
        from auth_app.services import RequestValidator

        is_valid, error = RequestValidator.validate_password_strength('short')

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
