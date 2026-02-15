import base64
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django_ratelimit.decorators import ratelimit

from auth_app.services import (
    RequestValidator,
    ResponseBuilder,
    get_auth_service,
    get_expense_repository,
    get_file_storage,
)

from .middleware import require_auth

logger = logging.getLogger(__name__)


@csrf_exempt
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def login_view(request):
    """Authenticate user and return tokens."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for login endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Validate required fields
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])
        if not is_valid:
            logger.warning(f"Login attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        # Use service layer (abstracts cloud vs local)
        auth_service = get_auth_service()
        tokens, error = auth_service.login(email, password)

        if error:
            logger.warning(f"Login failed for {email}: {error}")
            status_code = 401 if 'Invalid credentials' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"Successful login for user: {email}")

        # Build response with tokens
        response = ResponseBuilder.with_tokens(
            'Login successful',
            tokens['id_token'],
            tokens['refresh_token'],
            tokens['access_token'],
        )

        # Set access_token as HttpOnly cookie
        is_local = settings.IS_LOCAL_DEMO if hasattr(settings, 'IS_LOCAL_DEMO') else False
        response.set_cookie(
            key='access_token',
            value=tokens['access_token'],
            httponly=True,
            secure=not is_local,
            samesite='Lax' if is_local else 'None',
            path='/',
            max_age=60 * 60 * 24,  # 1 day
        )
        return response

    except json.JSONDecodeError:
        logger.error("Invalid JSON in login request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An unexpected error occurred', 500)


@csrf_exempt
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def signup_view(request):
    """Register a new user."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for signup endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)

        # Validate required fields
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'password'])
        if not is_valid:
            logger.warning(f"Signup attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        email = data.get('email')
        password = data.get('password')

        # Use service layer
        auth_service = get_auth_service()
        success, error = auth_service.signup(email, password)

        if not success:
            logger.warning(f"Signup failed for {email}: {error}")
            status_code = 409 if 'already exists' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"User signup successful: {email}")
        msg = 'Sign up successful! You can now log in.'
        return ResponseBuilder.success(msg, status=201)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in signup request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An unexpected error occurred', 500)


@csrf_exempt
def confirm_signup_view(request):
    """Confirm user signup with verification code."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for confirm-signup endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)

        is_valid, errors = RequestValidator.require_fields(data, ['email', 'code'])
        if not is_valid:
            logger.warning(f"Confirm signup attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        email = data.get('email')
        code = data.get('code')

        auth_service = get_auth_service()
        success, error = auth_service.confirm_signup(email, code)

        if not success:
            logger.warning(f"Confirmation failed for {email}: {error}")
            status_code = 404 if 'not found' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"User confirmed successfully: {email}")
        return ResponseBuilder.success('Account confirmed! You can now log in.')

    except json.JSONDecodeError:
        logger.error("Invalid JSON in confirm signup request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error during confirm signup: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An unexpected error occurred', 500)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL, block=True)
def forgot_password_view(request):
    """Initiate password reset flow."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for forgot-password endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        is_valid, errors = RequestValidator.require_fields(data, ['email'])
        if not is_valid:
            logger.warning(f"Forgot password attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        email = data.get('email')

        auth_service = get_auth_service()
        success, error = auth_service.forgot_password(email)

        if not success:
            logger.warning(f"Forgot password failed for {email}: {error}")
            status_code = 404 if 'not found' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"Password reset initiated for user: {email}")
        msg = 'Password reset code sent to your email.'
        return ResponseBuilder.success(msg)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in forgot password request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An unexpected error occurred', 500)


@csrf_exempt
def confirm_forgot_password_view(request):
    """Complete password reset with verification code."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for confirm-forgot-password endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        is_valid, errors = RequestValidator.require_fields(
            data, ['email', 'code', 'new_password']
        )
        if not is_valid:
            logger.warning(f"Confirm forgot password attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')

        auth_service = get_auth_service()
        success, error = auth_service.confirm_forgot_password(email, code, new_password)

        if not success:
            logger.warning(f"Confirm forgot password failed for {email}: {error}")
            status_code = 404 if 'not found' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"Password reset completed successfully for user: {email}")
        msg = 'Password reset successful! You can now log in with your new password.'
        return ResponseBuilder.success(msg)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in confirm forgot password request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(
            f"Unexpected error during password reset confirmation: {str(e)}", exc_info=True
        )
        return ResponseBuilder.error('An unexpected error occurred', 500)


@csrf_exempt
def verify_reset_code_view(request):
    """Verify password reset code validity."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for verify-reset-code endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        is_valid, errors = RequestValidator.require_fields(data, ['email', 'code'])
        if not is_valid:
            logger.warning(f"Verify reset code attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        email = data.get('email')
        code = data.get('code')

        auth_service = get_auth_service()
        valid, error = auth_service.verify_reset_code(email, code)

        if not valid:
            logger.warning(f"Reset code verification failed for {email}: {error}")
            status_code = 404 if 'not found' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"Reset code verified successfully for user: {email}")
        return ResponseBuilder.success('Reset code is valid.')

    except json.JSONDecodeError:
        logger.error("Invalid JSON in verify reset code request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error during verify reset code: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An unexpected error occurred', 500)


@require_auth
def add_expense(request):
    """Add a new expense."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for add expense endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        user_id = request.user_info['user_id']

        # Validate required fields
        is_valid, errors = RequestValidator.require_fields(data, ['amount', 'category'])
        if not is_valid:
            logger.warning(f"Add expense attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')

        # Validate amount is numeric
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            logger.warning(f"Invalid amount format: {amount}")
            return ResponseBuilder.error('Amount must be a valid number', 400)

        # Create expense using service layer
        expense_repo = get_expense_repository()
        expense = expense_repo.create(user_id, amount, category, description)

        logger.info(f"Expense added for user: {user_id}, amount: {amount}, category: {category}")

        return ResponseBuilder.success(
            'Expense added successfully',
            {
                'expense_id': expense['expense_id'],
                'id': expense['expense_id'],
                'user_id': expense['user_id'],
                'amount': str(expense['amount']),
                'category': expense['category'],
                'description': expense['description'],
                'timestamp': expense['timestamp'],
            },
            status=201,
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in add expense request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An error occurred while adding expense', 500)


@require_auth
def get_expenses(request):
    """Get expenses for a user."""
    if request.method != 'GET':
        logger.warning(f"Invalid method {request.method} for get expenses endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        user_id = request.user_info['user_id']

        # Get expenses using service layer
        expense_repo = get_expense_repository()
        expenses = expense_repo.get_by_user(user_id)

        expense_list = [
            {
                'id': exp['expense_id'],
                'user_id': exp['user_id'],
                'amount': str(exp['amount']),
                'category': exp['category'],
                'description': exp['description'],
                'timestamp': exp['timestamp'],
                'receipt_url': exp.get('receipt_url'),
            }
            for exp in expenses
        ]

        logger.info(f"Retrieved {len(expense_list)} expenses for user: {user_id}")

        return ResponseBuilder.success(
            'Expenses retrieved successfully',
            {'expenses': expense_list, 'count': len(expense_list)},
        )

    except Exception as e:
        logger.error(f"Error getting expenses: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An error occurred while retrieving expenses', 500)


@require_auth
def upload_receipt(request):
    """Upload a receipt file (to S3 in cloud mode, local mock in demo mode)."""
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for upload receipt endpoint")
        return ResponseBuilder.error('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        user_id = request.user_info['user_id']

        # Validate required fields
        is_valid, errors = RequestValidator.require_fields(data, ['file', 'filename'])
        if not is_valid:
            logger.warning(f"Receipt upload attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        file_data = data.get('file')
        file_name = data.get('filename')
        expense_id = data.get('expense_id')  # Optional

        # Validate and decode file data
        try:
            if file_data.startswith('data:'):
                header, encoded = file_data.split(',', 1)
                file_data = encoded

            file_bytes = base64.b64decode(file_data)
            if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"File too large: {len(file_bytes)} bytes")
                return ResponseBuilder.error('File size exceeds 10MB limit', 400)
        except Exception as e:
            logger.error(f"Error processing file data: {str(e)}")
            return ResponseBuilder.error('Invalid file data format', 400)

        # Upload using service layer
        file_storage = get_file_storage()
        file_url = file_storage.upload(file_name, file_bytes, user_id)

        logger.info(f"Receipt uploaded for user {user_id}: {file_name}")

        # Update expense with receipt URL if provided
        if expense_id:
            expense_repo = get_expense_repository()
            expense_repo.update_receipt_url(expense_id, file_url)
            logger.info(f"Receipt URL linked to expense: {expense_id}")

        return ResponseBuilder.success(
            'Receipt uploaded successfully',
            {
                'file_url': file_url,
                'file_name': file_name,
                'expense_id': expense_id,
            },
            status=201,
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in receipt upload request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Error uploading receipt: {str(e)}", exc_info=True)
        return ResponseBuilder.error('An error occurred while uploading receipt', 500)


@require_auth
@require_http_methods(["GET", "PUT"])
def profile_view(request):
    """Get or update user profile."""
    if request.method == 'GET':
        try:
            return ResponseBuilder.success('Profile retrieved', {'profile': request.user_info})
        except Exception as e:
            logger.error(f"Unexpected error getting profile: {str(e)}")
            return ResponseBuilder.error('An unexpected error occurred', 500)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = request.user_info['user_id']

            if not data:
                return ResponseBuilder.error('No fields to update', 400)

            auth_service = get_auth_service()
            profile, error = auth_service.update_user_profile(user_id, **data)

            if error:
                logger.warning(f"Failed to update profile for {user_id}: {error}")
                return ResponseBuilder.error(error, 500)

            logger.info(f"Profile updated for user: {user_id}")
            return ResponseBuilder.success('Profile updated successfully')

        except json.JSONDecodeError:
            logger.error("Invalid JSON in profile update request")
            return ResponseBuilder.error('Invalid JSON format', 400)
        except Exception as e:
            logger.error(f"Unexpected error updating profile: {str(e)}")
            return ResponseBuilder.error('An unexpected error occurred', 500)


@require_auth
@require_POST
def change_password_view(request):
    """Change the user's password."""
    try:
        data = json.loads(request.body)

        is_valid, errors = RequestValidator.require_fields(
            data, ['current_password', 'new_password']
        )
        if not is_valid:
            logger.warning(f"Change password attempt with missing fields: {errors}")
            return ResponseBuilder.validation_error(errors)

        user_id = request.user_info['user_id']
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        auth_service = get_auth_service()
        success, error = auth_service.change_password(user_id, current_password, new_password)

        if not success:
            logger.warning(f"Password change failed for {user_id}: {error}")
            status_code = 401 if 'incorrect' in error else 400
            return ResponseBuilder.error(error, status_code)

        logger.info(f"Password changed for user: {user_id}")
        return ResponseBuilder.success('Password changed successfully')

    except json.JSONDecodeError:
        logger.error("Invalid JSON in change password request")
        return ResponseBuilder.error('Invalid JSON format', 400)
    except Exception as e:
        logger.error(f"Unexpected error changing password: {str(e)}")
        return ResponseBuilder.error('An unexpected error occurred', 500)


def healthz(request):
    return JsonResponse({"status": "ok"})
