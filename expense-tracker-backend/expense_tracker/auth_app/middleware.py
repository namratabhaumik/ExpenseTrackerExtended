import base64
import json
import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.http import JsonResponse

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
            # Local demo mode: use simple token validation
            is_local_demo = settings.IS_LOCAL_DEMO if hasattr(settings, 'IS_LOCAL_DEMO') else False
            if is_local_demo:
                try:
                    # Decode mock token (base64 encoded JSON)
                    # Add padding back if it was stripped
                    padding = 4 - (len(token) % 4)
                    if padding != 4:
                        token = token + ('=' * padding)
                    payload = json.loads(base64.b64decode(token).decode())
                    user_email = payload.get('sub')  # 'sub' contains the email

                    request.user_info = {
                        'user_id': user_email.replace('@', '_').replace('.', '_'),
                        'email': user_email,
                        'name': user_email.split('@')[0]
                    }
                    logger.debug(f"Local demo auth successful for: {user_email}")
                    return self.get_response(request)
                except Exception as e:
                    logger.warning(f"Invalid local demo token: {str(e)}")
                    return JsonResponse({
                        'error': 'Invalid token',
                        'status': 'error'
                    }, status=401)

            # Production: Validate token with Cognito
            cognito_client = get_cognito_client()
            response = cognito_client.get_user(
                AccessToken=token
            )

            # Add user info to request
            user_attributes = response['UserAttributes']
            request.user_info = {
                'user_id': response['Username'],
                'email': next((attr['Value'] for attr in user_attributes if attr['Name'] == 'email'), None),
                'name': next((attr['Value'] for attr in user_attributes if attr['Name'] == 'name'), None)
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
