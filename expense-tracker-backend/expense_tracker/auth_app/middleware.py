import jwt
import json
import logging
from django.http import JsonResponse
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Lazy-load Cognito client
_cognito_client = None


def get_cognito_client():
    global _cognito_client
    if _cognito_client is None:
        _cognito_client = boto3.client(
            'cognito-idp', region_name=settings.AWS_REGION)
    return _cognito_client


class JWTAuthenticationMiddleware:
    """Middleware to validate JWT tokens from AWS Cognito."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for login, signup, confirm-signup, password reset, and health check endpoints
        if (request.path == '/api/login/' and request.method == 'POST') or \
           (request.path == '/api/signup/' and request.method == 'POST') or \
           (request.path == '/api/confirm-signup/' and request.method == 'POST') or \
           (request.path == '/api/forgot-password/' and request.method == 'POST') or \
           (request.path == '/api/confirm-forgot-password/' and request.method == 'POST') or \
           (request.path == '/api/verify-reset-code/' and request.method == 'POST') or \
           (request.path == '/api/healthz/'):
            return self.get_response(request)

        # Try to get token from Authorization header first
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Fallback to cookie-based authentication
            token = request.COOKIES.get('access_token')
            if not token:
                return JsonResponse({
                    'error': 'Authentication token missing',
                    'status': 'error'
                }, status=401)

        try:
            # Validate token with Cognito
            cognito_client = get_cognito_client()
            response = cognito_client.get_user(
                AccessToken=token
            )

            # Add user info to request
            request.user_info = {
                'user_id': response['Username'],
                'email': next((attr['Value'] for attr in response['UserAttributes'] if attr['Name'] == 'email'), None)
            }

            return self.get_response(request)

        except ClientError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return JsonResponse({
                'error': 'Invalid or expired token',
                'status': 'error'
            }, status=401)
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return JsonResponse({
                'error': 'Authentication failed',
                'status': 'error'
            }, status=500)


def require_auth(view_func):
    """Decorator to require authentication for views."""
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user_info'):
            return JsonResponse({
                'error': 'Authentication required',
                'status': 'error'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
