"""Unified response building and error handling."""

from typing import Dict, Optional, Tuple

from botocore.exceptions import ClientError
from django.http import JsonResponse


class ErrorMapper:
    """Centralized error code mapping and standardization."""

    # Cognito error code mappings
    COGNITO_ERROR_MAP = {
        'NotAuthorizedException': ('Invalid credentials', 401),
        'UserNotFoundException': ('User does not exist', 404),
        'UsernameExistsException': ('User already exists', 409),
        'InvalidPasswordException': ('Password does not meet requirements', 400),
        'InvalidParameterException': ('Invalid parameter', 400),
        'CodeMismatchException': ('Invalid confirmation code', 400),
        'ExpiredCodeException': ('Confirmation code expired', 400),
        'LimitExceededException': ('Too many attempts, please try again later', 429),
        'PasswordResetRequiredException': ('Password reset is required', 400),
        'TooManyRequestsException': ('Too many requests, please try again later', 429),
    }

    @staticmethod
    def map_cognito_error(error: ClientError) -> Tuple[str, int]:
        """
        Map Cognito error codes to user-friendly messages and HTTP status codes.

        Args:
            error: botocore ClientError

        Returns:
            (error_message, status_code)
        """
        error_code = error.response['Error']['Code']
        message, status = ErrorMapper.COGNITO_ERROR_MAP.get(
            error_code, ('An unexpected error occurred', 500)
        )
        return message, status

    @staticmethod
    def map_validation_error(field: str, reason: str) -> Tuple[str, int]:
        """
        Map validation errors to messages and status codes.

        Args:
            field: Field that failed validation
            reason: Reason for validation failure

        Returns:
            (error_message, status_code)
        """
        message = f"Validation error: {field} - {reason}"
        return message, 400

    @staticmethod
    def map_generic_error(exception: Exception) -> Tuple[str, int]:
        """
        Map generic exceptions to status codes.

        Args:
            exception: The exception that occurred

        Returns:
            (error_message, status_code)
        """
        if isinstance(exception, ClientError):
            return ErrorMapper.map_cognito_error(exception)

        if isinstance(exception, ValueError):
            return str(exception), 400

        if isinstance(exception, PermissionError):
            return 'Unauthorized', 403

        return 'An unexpected error occurred', 500


class ResponseBuilder:
    """Build consistent JSON responses."""

    @staticmethod
    def success(
        message: str, data: Optional[Dict] = None, status: int = 200
    ) -> JsonResponse:
        """
        Build a success response.

        Args:
            message: Success message
            data: Optional response data
            status: HTTP status code

        Returns:
            JsonResponse with success format
        """
        response_data = {
            'status': 'success',
            'message': message,
        }
        if data:
            response_data['data'] = data

        return JsonResponse(response_data, status=status)

    @staticmethod
    def error(message: str, status: int = 400) -> JsonResponse:
        """
        Build an error response.

        Args:
            message: Error message
            status: HTTP status code

        Returns:
            JsonResponse with error format
        """
        return JsonResponse(
            {
                'status': 'error',
                'error': message,
            },
            status=status,
        )

    @staticmethod
    def with_tokens(
        message: str,
        id_token: str,
        refresh_token: str,
        access_token: str,
        status: int = 200,
    ) -> JsonResponse:
        """
        Build a success response with auth tokens.

        Args:
            message: Success message
            id_token: ID token
            refresh_token: Refresh token
            access_token: Access token (set as cookie separately)
            status: HTTP status code

        Returns:
            JsonResponse with tokens in body (access_token should be in cookie)
        """
        return JsonResponse(
            {
                'status': 'success',
                'message': message,
                'id_token': id_token,
                'refresh_token': refresh_token,
            },
            status=status,
        )

    @staticmethod
    def validation_error(errors: Dict[str, str]) -> JsonResponse:
        """
        Build a validation error response.

        Args:
            errors: Dictionary of field -> error message

        Returns:
            JsonResponse with validation errors
        """
        return JsonResponse(
            {
                'status': 'error',
                'error': 'Validation failed',
                'errors': errors,
            },
            status=400,
        )


class RequestValidator:
    """Common request validation helpers."""

    @staticmethod
    def require_fields(data: Dict, required: list) -> Tuple[bool, Optional[Dict]]:
        """
        Validate that required fields are present in request data.

        Args:
            data: Request data dictionary
            required: List of required field names

        Returns:
            (is_valid, error_dict or None)
        """
        errors = {}
        for field in required:
            if not data.get(field):
                errors[field] = f'{field} is required'

        if errors:
            return False, errors

        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.

        Args:
            email: Email string

        Returns:
            (is_valid, error_message or None)
        """
        if not email or '@' not in email:
            return False, 'Invalid email format'
        return True, None

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password meets minimum requirements.

        Args:
            password: Password string

        Returns:
            (is_valid, error_message or None)
        """
        if not password:
            return False, 'Password is required'

        if len(password) < 8:
            return False, 'Password must be at least 8 characters'

        return True, None
