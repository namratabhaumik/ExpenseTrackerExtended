"""Unit tests for response_service module (ErrorMapper, ResponseBuilder, RequestValidator)."""

import json
from unittest.mock import Mock

from botocore.exceptions import ClientError
from django.test import TestCase

from auth_app.services.response_service import (
    ErrorMapper,
    RequestValidator,
    ResponseBuilder,
)


def get_response_data(response):
    """Extract JSON data from a JsonResponse object."""
    return json.loads(response.content.decode())


class ErrorMapperTest(TestCase):
    """Test error code mapping and standardization."""

    def test_map_cognito_not_authorized(self):
        """Test mapping NotAuthorizedException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'NotAuthorizedException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Invalid credentials')
        self.assertEqual(status, 401)

    def test_map_cognito_user_not_found(self):
        """Test mapping UserNotFoundException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'UserNotFoundException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'User does not exist')
        self.assertEqual(status, 404)

    def test_map_cognito_user_exists(self):
        """Test mapping UsernameExistsException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'UsernameExistsException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'User already exists')
        self.assertEqual(status, 409)

    def test_map_cognito_invalid_password(self):
        """Test mapping InvalidPasswordException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'InvalidPasswordException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Password does not meet requirements')
        self.assertEqual(status, 400)

    def test_map_cognito_code_mismatch(self):
        """Test mapping CodeMismatchException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'CodeMismatchException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Invalid confirmation code')
        self.assertEqual(status, 400)

    def test_map_cognito_expired_code(self):
        """Test mapping ExpiredCodeException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'ExpiredCodeException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Confirmation code expired')
        self.assertEqual(status, 400)

    def test_map_cognito_limit_exceeded(self):
        """Test mapping LimitExceededException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'LimitExceededException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Too many attempts, please try again later')
        self.assertEqual(status, 429)

    def test_map_cognito_too_many_requests(self):
        """Test mapping TooManyRequestsException"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'TooManyRequestsException'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'Too many requests, please try again later')
        self.assertEqual(status, 429)

    def test_map_cognito_unknown_error(self):
        """Test mapping unknown Cognito error code"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'UnknownErrorCode'}
        }

        message, status = ErrorMapper.map_cognito_error(error)
        self.assertEqual(message, 'An unexpected error occurred')
        self.assertEqual(status, 500)

    def test_map_validation_error(self):
        """Test mapping validation errors"""
        message, status = ErrorMapper.map_validation_error('email', 'Invalid format')
        self.assertIn('email', message)
        self.assertIn('Invalid format', message)
        self.assertEqual(status, 400)

    def test_map_generic_error_client_error(self):
        """Test mapping generic ClientError"""
        error = Mock(spec=ClientError)
        error.response = {
            'Error': {'Code': 'NotAuthorizedException'}
        }

        message, status = ErrorMapper.map_generic_error(error)
        self.assertEqual(message, 'Invalid credentials')
        self.assertEqual(status, 401)

    def test_map_generic_error_value_error(self):
        """Test mapping ValueError"""
        error = ValueError('Invalid value')

        message, status = ErrorMapper.map_generic_error(error)
        self.assertEqual(message, 'Invalid value')
        self.assertEqual(status, 400)

    def test_map_generic_error_permission_error(self):
        """Test mapping PermissionError"""
        error = PermissionError('Not allowed')

        message, status = ErrorMapper.map_generic_error(error)
        self.assertEqual(message, 'Unauthorized')
        self.assertEqual(status, 403)

    def test_map_generic_error_unknown(self):
        """Test mapping unknown exception"""
        error = RuntimeError('Something went wrong')

        message, status = ErrorMapper.map_generic_error(error)
        self.assertEqual(message, 'An unexpected error occurred')
        self.assertEqual(status, 500)


class ResponseBuilderTest(TestCase):
    """Test response building utilities."""

    def test_success_response_simple(self):
        """Test building simple success response"""
        response = ResponseBuilder.success('Operation completed')

        self.assertEqual(response.status_code, 200)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Operation completed')
        self.assertNotIn('data', data)

    def test_success_response_with_data(self):
        """Test building success response with data"""
        test_data = {'user_id': 123, 'email': 'test@example.com'}
        response = ResponseBuilder.success('User created', data=test_data)

        self.assertEqual(response.status_code, 200)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'User created')
        self.assertEqual(data['data'], test_data)

    def test_success_response_custom_status(self):
        """Test building success response with custom status code"""
        response = ResponseBuilder.success('Created', status=201)

        self.assertEqual(response.status_code, 201)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'success')

    def test_error_response(self):
        """Test building error response"""
        response = ResponseBuilder.error('Operation failed')

        self.assertEqual(response.status_code, 400)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error'], 'Operation failed')

    def test_error_response_custom_status(self):
        """Test building error response with custom status code"""
        response = ResponseBuilder.error('Not found', status=404)

        self.assertEqual(response.status_code, 404)
        data = get_response_data(response)
        self.assertEqual(data['error'], 'Not found')

    def test_with_tokens_response(self):
        """Test building response with auth tokens"""
        response = ResponseBuilder.with_tokens(
            'Login successful',
            id_token='id_123',
            refresh_token='refresh_123',
            access_token='access_123'
        )

        self.assertEqual(response.status_code, 200)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Login successful')
        self.assertEqual(data['id_token'], 'id_123')
        self.assertEqual(data['refresh_token'], 'refresh_123')
        self.assertNotIn('access_token', data)  # Should be in cookie

    def test_with_tokens_custom_status(self):
        """Test with_tokens response with custom status"""
        response = ResponseBuilder.with_tokens(
            'Created',
            id_token='id_123',
            refresh_token='refresh_123',
            access_token='access_123',
            status=201
        )

        self.assertEqual(response.status_code, 201)

    def test_validation_error_response(self):
        """Test building validation error response"""
        errors = {
            'email': 'Invalid email format',
            'password': 'Password too short'
        }
        response = ResponseBuilder.validation_error(errors)

        self.assertEqual(response.status_code, 400)
        data = get_response_data(response)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error'], 'Validation failed')
        self.assertEqual(data['errors'], errors)


class RequestValidatorTest(TestCase):
    """Test request validation utilities."""

    def test_require_fields_all_present(self):
        """Test validation when all required fields are present"""
        data = {'email': 'test@example.com', 'password': 'secret123'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertTrue(is_valid)
        self.assertIsNone(errors)

    def test_require_fields_missing_field(self):
        """Test validation when a required field is missing"""
        data = {'email': 'test@example.com'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertFalse(is_valid)
        self.assertIsNotNone(errors)
        self.assertIn('password', errors)

    def test_require_fields_empty_field(self):
        """Test validation when a required field is empty"""
        data = {'email': '', 'password': 'secret123'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertFalse(is_valid)
        self.assertIn('email', errors)

    def test_require_fields_none_field(self):
        """Test validation when a required field is None"""
        data = {'email': None, 'password': 'secret123'}
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])

        self.assertFalse(is_valid)
        self.assertIn('email', errors)

    def test_require_fields_multiple_missing(self):
        """Test validation when multiple fields are missing"""
        data = {'email': 'test@example.com'}
        is_valid, errors = RequestValidator.require_fields(
            data, ['email', 'password', 'name']
        )

        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)
        self.assertIn('password', errors)
        self.assertIn('name', errors)

    def test_validate_email_valid(self):
        """Test email validation with valid email"""
        is_valid, error = RequestValidator.validate_email('test@example.com')

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_email_invalid_no_at(self):
        """Test email validation without @ symbol"""
        is_valid, error = RequestValidator.validate_email('notanemail')

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_email_empty(self):
        """Test email validation with empty string"""
        is_valid, error = RequestValidator.validate_email('')

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_email_none(self):
        """Test email validation with None"""
        is_valid, error = RequestValidator.validate_email(None)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_password_valid(self):
        """Test password validation with valid password"""
        is_valid, error = RequestValidator.validate_password_strength('SecurePass123!')

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_password_empty(self):
        """Test password validation with empty password"""
        is_valid, error = RequestValidator.validate_password_strength('')

        self.assertFalse(is_valid)
        self.assertIn('required', error)

    def test_validate_password_too_short(self):
        """Test password validation with short password"""
        is_valid, error = RequestValidator.validate_password_strength('short')

        self.assertFalse(is_valid)
        self.assertIn('8 characters', error)

    def test_validate_password_minimum_length(self):
        """Test password validation at minimum length (8 chars)"""
        is_valid, error = RequestValidator.validate_password_strength('12345678')

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_password_none(self):
        """Test password validation with None"""
        is_valid, error = RequestValidator.validate_password_strength(None)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
