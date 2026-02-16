"""Local demo mode authentication service (no AWS Cognito)."""

import base64
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from auth_app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


def create_mock_tokens(email: str) -> str:
    """Create mock JWT tokens for local development."""
    payload = {
        'sub': email,
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int(datetime.utcnow().timestamp()) + 86400,  # 24 hours
    }
    # Simple base64 encoding (NOT secure, for demo only)
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    return token


class LocalAuthService(AuthService):
    """Authentication service using local mock authentication."""

    def login(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Mock login for local development - accepts any email/password.

        Returns:
            (tokens_dict, error_message)
        """
        try:
            if not email or not password:
                return None, 'Missing required fields: email and password'

            # In local mode, accept any credentials
            id_token = create_mock_tokens(email)
            access_token = create_mock_tokens(email)
            refresh_token = create_mock_tokens(email)

            logger.info(f'Local demo login for user: {email}')

            return (
                {
                    'id_token': id_token,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                },
                None,
            )

        except Exception as e:
            logger.error(f'Unexpected error during login: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'

    def signup(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Mock signup for local development - auto-confirms users.

        Returns:
            (success, error_message)
        """
        try:
            if not email or not password:
                return False, 'Missing required fields: email and password'

            # In local mode, accept any email format
            if email and '@' in email:
                logger.info(f'Local demo signup for user: {email}')
                return True, None

            return False, 'Invalid email format'

        except Exception as e:
            logger.error(f'Unexpected error during signup: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def confirm_signup(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Mock signup confirmation for local development.

        In local mode, all codes are accepted as valid.
        """
        try:
            if not email or not code:
                return False, 'Missing required fields: email and code'

            logger.info(f'Local demo signup confirmation for user: {email}')
            return True, None

        except Exception as e:
            logger.error(f'Unexpected error during confirmation: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def forgot_password(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Mock password reset initiation for local development.

        In local mode, pretend to send reset code.
        """
        try:
            if not email:
                return False, 'Missing required field: email'

            logger.info(f'Mock password reset initiated for user: {email}')
            return True, None

        except Exception as e:
            logger.error(f'Unexpected error during forgot password: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def confirm_forgot_password(
        self, email: str, code: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Mock password reset completion for local development.

        In local mode, any code is accepted.
        """
        try:
            if not email or not code or not new_password:
                return False, 'Missing required fields: email, code, and password'

            logger.info(f'Mock password reset completed for user: {email}')
            return True, None

        except Exception as e:
            logger.error(
                f'Unexpected error during confirm forgot password: {str(e)}', exc_info=True
            )
            return False, 'An unexpected error occurred'

    def verify_reset_code(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Mock reset code verification for local development.

        In local mode, any code is valid.
        """
        try:
            if not email or not code:
                return False, 'Missing required fields: email and code'

            logger.info(f'Mock reset code verification for user: {email}')
            return True, None

        except Exception as e:
            logger.error(f'Unexpected error during verify reset code: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Mock password change for local development.

        In local mode, no validation is performed.
        """
        try:
            if not user_id or not old_password or not new_password:
                return False, 'Missing required fields'

            logger.info(f'Mock password change for user: {user_id}')
            return True, None

        except Exception as e:
            logger.error(f'Unexpected error during change password: {str(e)}', exc_info=True)
            return False, 'An unexpected error occurred'

    def get_user_profile(self, user_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Mock user profile retrieval for local development.

        Returns a basic profile with minimal information.
        """
        try:
            if not user_id:
                return None, 'Missing required field: user_id'

            profile = {
                'user_id': user_id,
                'email': user_id,
                'email_verified': True,
            }

            logger.info(f'Mock user profile retrieved for user: {user_id}')
            return profile, None

        except Exception as e:
            logger.error(f'Unexpected error getting user profile: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'

    def update_user_profile(
        self, user_id: str, **kwargs
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Mock user profile update for local development.

        In local mode, updates are accepted but not persisted.
        """
        try:
            if not user_id:
                return None, 'Missing required field: user_id'

            profile = {
                'user_id': user_id,
                'email': kwargs.get('email', user_id),
                'email_verified': True,
            }

            logger.info(f'Mock user profile updated for user: {user_id}')
            return profile, None

        except Exception as e:
            logger.error(f'Unexpected error updating user profile: {str(e)}', exc_info=True)
            return None, 'An unexpected error occurred'
