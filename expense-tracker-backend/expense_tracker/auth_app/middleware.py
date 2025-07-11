import jwt
import json
import logging
from django.http import JsonResponse
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """Middleware to validate JWT tokens from AWS Cognito."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.cognito_client = boto3.client(
            'cognito-idp', region_name=settings.AWS_REGION)

    def __call__(self, request):
        # Skip authentication for login, signup, confirm-signup, and health check endpoints
        if (request.path == '/api/login/' and request.method == 'POST') or \
           (request.path == '/api/signup/' and request.method == 'POST') or \
           (request.path == '/api/confirm-signup/' and request.method == 'POST') or \
           (request.path == '/api/healthz/'):
            return self.get_response(request)

        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Authorization header required',
                'status': 'error'
            }, status=401)

        token = auth_header.split(' ')[1]

        try:
            # Validate token with Cognito
            response = self.cognito_client.get_user(
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
