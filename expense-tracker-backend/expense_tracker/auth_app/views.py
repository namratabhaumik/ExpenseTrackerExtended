"""
Session-based authentication views for traditional web app.
Uses Django's built-in authentication + CSRF protection.
"""
import json
import logging
import base64

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django_ratelimit.decorators import ratelimit

from auth_app.services import (
    get_expense_repository,
    get_file_storage,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def signup_view(request):
    """Register a new user using Django's built-in User model."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password required'}, status=400)

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'User already exists'}, status=409)

        # Create user with email as username
        user = User.objects.create_user(username=email, email=email, password=password)
        logger.info(f"User registered: {email}")

        return JsonResponse({
            'status': 'success',
            'message': 'Sign up successful! You can now log in.',
            'user_id': user.id,
            'email': user.email
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({'error': 'Registration failed'}, status=500)


def confirm_signup_view(request):
    """Placeholder for signup confirmation (not needed for session auth)."""
    return JsonResponse({'message': 'Already confirmed'})


def forgot_password_view(request):
    """Placeholder for forgot password (can implement email reset later)."""
    return JsonResponse({'message': 'Check email for reset link'})


def confirm_forgot_password_view(request):
    """Placeholder for confirm forgot password."""
    return JsonResponse({'message': 'Password reset'})


def verify_reset_code_view(request):
    """Placeholder for verify reset code."""
    return JsonResponse({'message': 'Code verified'})


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def login_view(request):
    """Authenticate user and create session."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password required'}, status=400)

        # Authenticate using Django's auth
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)  # Creates session cookie
            logger.info(f"User logged in: {email}")

            # Get CSRF token for frontend
            csrf_token = get_token(request)

            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'user_id': user.id,
                'email': user.email,
                'csrf_token': csrf_token
            })
        else:
            logger.warning(f"Failed login attempt for: {email}")
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({'error': 'Login failed'}, status=500)


@require_http_methods(["POST"])
def logout_view(request):
    """Logout user and destroy session."""
    logout(request)
    logger.info("User logged out")
    return JsonResponse({'message': 'Logged out'})


@csrf_exempt
@require_http_methods(["GET"])
def csrf_token_view(request):
    """Return CSRF token for frontend to use in requests."""
    token = get_token(request)
    return JsonResponse({'csrf_token': token})


@login_required(login_url='/api/login/')
@require_http_methods(["GET", "PUT"])
def profile_view(request):
    """Get or update user profile."""
    if request.method == 'GET':
        return JsonResponse({
            'profile': {
                'user_id': request.user.id,
                'email': request.user.email,
                'name': request.user.first_name or request.user.username.split('@')[0]
            }
        })
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            request.user.first_name = data.get('name', request.user.first_name)
            request.user.save()
            return JsonResponse({'message': 'Profile updated'})
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return JsonResponse({'error': 'Update failed'}, status=500)


@login_required(login_url='/api/login/')
@require_POST
def change_password_view(request):
    """Change user password."""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return JsonResponse({'error': 'Both passwords required'}, status=400)

        # Verify current password
        if not request.user.check_password(current_password):
            return JsonResponse({'error': 'Current password incorrect'}, status=401)

        # Set new password
        request.user.set_password(new_password)
        request.user.save()

        logger.info(f"Password changed for: {request.user.email}")

        # Log out the user for security - they must log back in with new password
        logout(request)

        return JsonResponse({'message': 'Password changed successfully. Please log in with your new password.'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return JsonResponse({'error': 'Change failed'}, status=500)


@login_required(login_url='/api/login/')
@require_http_methods(["POST"])
def add_expense(request):
    """Add a new expense."""
    try:
        data = json.loads(request.body)
        user_id = request.user.id

        # Validate required fields
        if not data.get('amount') or not data.get('category'):
            return JsonResponse({'error': 'Amount and category required'}, status=400)

        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')

        # Use service layer
        expense_repo = get_expense_repository()
        expense = expense_repo.create(
            user_id=user_id,
            amount=amount,
            category=category,
            description=description
        )

        logger.info(f"Expense added for user {user_id}: ${amount} in {category}")

        return JsonResponse(expense, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        return JsonResponse({'error': 'Failed to add expense'}, status=500)


@login_required(login_url='/api/login/')
@require_http_methods(["GET"])
def get_expenses(request):
    """Get expenses for a user."""
    try:
        user_id = request.user.id

        # Use service layer
        expense_repo = get_expense_repository()
        expenses = expense_repo.get_by_user(user_id)

        logger.info(f"Retrieved {len(expenses)} expenses for user {user_id}")

        return JsonResponse({'expenses': expenses})

    except Exception as e:
        logger.error(f"Error retrieving expenses: {str(e)}")
        return JsonResponse({'error': 'Failed to retrieve expenses'}, status=500)


@login_required(login_url='/api/login/')
@require_http_methods(["POST"])
def upload_receipt(request):
    """Upload a receipt file."""
    try:
        data = json.loads(request.body)
        user_id = request.user.id

        # Validate required fields
        if not data.get('file') or not data.get('filename'):
            return JsonResponse({
                'error': 'Validation failed',
                'errors': {'file': 'file is required', 'filename': 'filename is required'}
            }, status=400)

        file_data = data.get('file')
        file_name = data.get('filename')
        expense_id = data.get('expense_id')

        # Validate and decode file data
        try:
            if file_data.startswith('data:'):
                header, encoded = file_data.split(',', 1)
                file_data = encoded

            file_bytes = base64.b64decode(file_data)
            if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
                return JsonResponse({'error': 'File too large (max 10MB)'}, status=400)
        except Exception as e:
            logger.error(f"File decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid file format'}, status=400)

        # Use service layer for file storage
        file_storage = get_file_storage()
        file_url = file_storage.upload(file_name, file_bytes, user_id)

        logger.info(f"Receipt uploaded for user {user_id}: {file_name}")

        # Update expense with receipt URL if expense_id provided
        if expense_id:
            try:
                expense_repo = get_expense_repository()
                expense_repo.update_receipt_url(expense_id, file_url)
                logger.info(f"Receipt URL saved to expense {expense_id}")
            except Exception as e:
                logger.error(f"Error updating expense receipt URL: {str(e)}")
                return JsonResponse({'error': 'Receipt uploaded but could not link to expense'}, status=500)

        return JsonResponse({
            'file_url': file_url,
            'file_name': file_name,
            'expense_id': expense_id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error uploading receipt: {str(e)}")
        return JsonResponse({'error': 'Upload failed'}, status=500)


@require_http_methods(["GET"])
def healthz(request):
    """Health check endpoint."""
    return JsonResponse({'status': 'ok'})
