"""Abstract authentication service interface and factory."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

from django.conf import settings


class AuthService(ABC):
    """Abstract interface for authentication operations."""

    @abstractmethod
    def login(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user and return tokens.

        Returns:
            (tokens_dict, error_message) - tokens_dict is None if error occurred
        """
        pass

    @abstractmethod
    def signup(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Register a new user.

        Returns:
            (success, error_message) - error_message is None if successful
        """
        pass

    @abstractmethod
    def confirm_signup(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Confirm user signup with verification code.

        Returns:
            (success, error_message)
        """
        pass

    @abstractmethod
    def forgot_password(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Initiate password reset flow.

        Returns:
            (success, error_message)
        """
        pass

    @abstractmethod
    def confirm_forgot_password(
        self, email: str, code: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Complete password reset with verification code.

        Returns:
            (success, error_message)
        """
        pass

    @abstractmethod
    def verify_reset_code(self, email: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify password reset code validity.

        Returns:
            (valid, error_message)
        """
        pass

    @abstractmethod
    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password.

        Returns:
            (success, error_message)
        """
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Retrieve user profile information.

        Returns:
            (profile_dict, error_message)
        """
        pass

    @abstractmethod
    def update_user_profile(
        self, user_id: str, **kwargs
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Update user profile information.

        Returns:
            (updated_profile, error_message)
        """
        pass


def get_auth_service() -> AuthService:
    """
    Factory function to get appropriate auth service based on environment.

    Returns:
        LocalAuthService if IS_LOCAL_DEMO=true, else CognitoAuthService
    """
    is_local_demo = settings.IS_LOCAL_DEMO if hasattr(settings, 'IS_LOCAL_DEMO') else False

    if is_local_demo:
        from local_app.implementations.local_auth_service import LocalAuthService
        return LocalAuthService()
    else:
        from cloud_app.implementations.cognito_service import CognitoAuthService
        return CognitoAuthService()
