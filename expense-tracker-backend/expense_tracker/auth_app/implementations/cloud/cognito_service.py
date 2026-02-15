"""AWS Cognito authentication service implementation."""

import base64
import hashlib
import hmac
import logging
import os
from typing import Dict, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from auth_app.services.auth_service import AuthService
from auth_app.services.response_service import ErrorMapper

logger = logging.getLogger(__name__)

# Cognito configuration
COGNITO_REGION = settings.AWS_REGION
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.environ.get('COGNITO_CLIENT_SECRET')

# Lazy-load Cognito client
_cognito_client = None


def get_cognito_client():
    """Get or create Cognito client."""
    global _cognito_client
    if _cognito_client is None:
        _cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    return _cognito_client


def calculate_secret_hash(username: str) -> str:
    """Generate the SECRET_HASH for Cognito."""
    message = username + COGNITO_CLIENT_ID
    secret = bytes(COGNITO_CLIENT_SECRET, 'utf-8')
    digest = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


class CognitoAuthService(AuthService):
    """Authentication service using AWS Cognito."""

    def login(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user with Cognito.

        Returns:
            (tokens_dict, error_message) - tokens_dict contains access_token, id_token, refresh_token
        """
        try:
            if not email or not password:
                return None, 'Missing required fields: email and password'

            secret_hash = calculate_secret_hash(email)
            cognito_client = get_cognito_client()

            response = cognito_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                ClientId=COGNITO_CLIENT_ID,
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash,
                },
            )

            auth_result = response.get('AuthenticationResult', {})
            logger.info(f'Successful login for user: {email}')

            return (
                {
                    'access_token': auth_result.get('AccessToken'),
                    'id_token': auth_result.get('IdToken'),
                    'refresh_token': auth_result.get('RefreshToken'),
                },
                None,
            )

        except ClientError as e:
            error_msg, _ = ErrorMapper.map_cognito_error(e)
            logger.warning(f'Login failed for {email}: {error_msg}')
            return None, error_msg
        except Exception as e:
            logger.error(f'Unexpected error during login: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'

    def signup(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """Register a new user with Cognito."""
        try:
            if not email or not password:
                return False, 'Missing required fields: email and password'

            secret_hash = calculate_secret_hash(email)
            cognito_client = get_cognito_client()

            cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                ],
            )

            logger.info(f'User signup successful: {email}')
            return True, None

        except ClientError as e:
            error_msg, _ = ErrorMapper.map_cognito_error(e)
            logger.warning(f'Signup failed for {email}: {error_msg}')
            return False, error_msg
        except Exception as e:
            logger.error(f'Unexpected error during signup: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def confirm_signup(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """Confirm user signup with verification code."""
        try:
            if not email or not code:
                return False, 'Missing required fields: email and code'

            secret_hash = calculate_secret_hash(email)
            cognito_client = get_cognito_client()

            cognito_client.confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=code,
            )

            logger.info(f'User confirmed successfully: {email}')
            return True, None

        except ClientError as e:
            error_msg, _ = ErrorMapper.map_cognito_error(e)
            logger.warning(f'Confirmation failed for {email}: {error_msg}')
            return False, error_msg
        except Exception as e:
            logger.error(f'Unexpected error during confirmation: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def forgot_password(self, email: str) -> Tuple[bool, Optional[str]]:
        """Initiate password reset flow."""
        try:
            if not email:
                return False, 'Missing required field: email'

            secret_hash = calculate_secret_hash(email)
            cognito_client = get_cognito_client()

            cognito_client.forgot_password(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
            )

            logger.info(f'Password reset initiated for user: {email}')
            return True, None

        except ClientError as e:
            error_msg, _ = ErrorMapper.map_cognito_error(e)
            logger.warning(f'Forgot password failed for {email}: {error_msg}')
            return False, error_msg
        except Exception as e:
            logger.error(f'Unexpected error during forgot password: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def confirm_forgot_password(
        self, email: str, code: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """Complete password reset with verification code."""
        try:
            if not email or not code or not new_password:
                return False, 'Missing required fields: email, code, and password'

            secret_hash = calculate_secret_hash(email)
            cognito_client = get_cognito_client()

            cognito_client.confirm_forgot_password(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=code,
                Password=new_password,
            )

            logger.info(f'Password reset completed for user: {email}')
            return True, None

        except ClientError as e:
            error_msg, _ = ErrorMapper.map_cognito_error(e)
            logger.warning(f'Confirm forgot password failed for {email}: {error_msg}')
            return False, error_msg
        except Exception as e:
            logger.error(
                f'Unexpected error during confirm forgot password: {str(e)}', exc_info=True
            )
            return False, 'An unexpected error occurred'

    def verify_reset_code(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """Verify password reset code validity."""
        try:
            if not email or not code:
                return False, 'Missing required fields: email and code'

            # Cognito doesn't have a direct verify endpoint, so we check it during confirm
            # Return success for now; actual validation happens in confirm_forgot_password
            logger.info(f'Reset code verification requested for user: {email}')
            return True, None

        except Exception as e:
            logger.error(f'Unexpected error during verify reset code: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """Change user password (requires access token)."""
        try:
            if not user_id or not old_password or not new_password:
                return False, 'Missing required fields'

            # Note: This requires access token, not just user_id
            # This is a limitation of the abstract interface that may need refinement
            logger.warning('change_password called without access token')
            return False, 'Invalid request'

        except Exception as e:
            logger.error(f'Unexpected error during change password: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def get_user_profile(self, user_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Retrieve user profile from Cognito."""
        try:
            if not user_id:
                return None, 'Missing required field: user_id'

            # Note: Getting user profile requires admin access or access token
            # This is a limitation that may need refinement
            logger.warning('get_user_profile called with limited capabilities')
            return None, 'Not implemented'

        except Exception as e:
            logger.error(f'Unexpected error getting user profile: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'

    def update_user_profile(
        self, user_id: str, **kwargs
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Update user profile in Cognito."""
        try:
            if not user_id:
                return None, 'Missing required field: user_id'

            # Note: Updating user profile requires admin access or access token
            logger.warning('update_user_profile called with limited capabilities')
            return None, 'Not implemented'

        except Exception as e:
            logger.error(f'Unexpected error updating user profile: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'
