import boto3
import json
import hmac
import hashlib
import base64
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
import os
from .middleware import require_auth
from .services.DynamoDBExpenseService import DynamoDBExpenseService
from botocore.exceptions import ClientError

from django.views.decorators.http import require_GET, require_POST, require_http_methods

from django.conf import settings

# Get logger for this module
logger = logging.getLogger(__name__)

# Cognito configuration
COGNITO_REGION = settings.AWS_REGION
COGNITO_CLIENT_ID = settings.COGNITO_CLIENT_ID
COGNITO_CLIENT_SECRET = settings.COGNITO_CLIENT_SECRET

# Lazy-load Cognito client
_cognito_client = None


def get_cognito_client():
    global _cognito_client
    if _cognito_client is None:
        _cognito_client = boto3.client(
            'cognito-idp', region_name=COGNITO_REGION)
    return _cognito_client


def calculate_secret_hash(username):
    """Generate the SECRET_HASH for Cognito."""
    message = username + COGNITO_CLIENT_ID
    secret = bytes(COGNITO_CLIENT_SECRET, 'utf-8')
    digest = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


@csrf_exempt
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def login_view(request):
    if request.method == 'POST':
        try:
            # Get the email and password from the request body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Validate required fields
            if not email or not password:
                logger.warning(
                    f"Login attempt with missing credentials: email={bool(email)}")
                return JsonResponse({
                    'error': 'Missing required fields: email and password',
                    'status': 'error'
                }, status=400)

            # Calculate the secret hash
            secret_hash = calculate_secret_hash(email)

            # Authenticate user with Cognito
            cognito_client = get_cognito_client()
            response = cognito_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                ClientId=COGNITO_CLIENT_ID,
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash,
                }
            )

            # If successful, return the tokens
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']

            logger.info(f"Successful login for user: {email}")
            response = JsonResponse({
                'message': 'Login successful',
                'id_token': id_token,
                'refresh_token': refresh_token,
                'status': 'success'
            })
            # Set access_token as HttpOnly, Secure cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Must be True for SameSite='None'
                samesite='None',  # Required for cross-domain cookies
                path='/',
                max_age=60*60*24  # 1 day
            )
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                logger.warning(f"Invalid credentials for user: {email}")
                return JsonResponse({
                    'error': 'Invalid credentials',
                    'status': 'error'
                }, status=401)
            elif error_code == 'UserNotFoundException':
                logger.warning(f"User not found: {email}")
                return JsonResponse({
                    'error': 'User does not exist',
                    'status': 'error'
                }, status=404)
            else:
                logger.error(f"Unexpected Cognito error: {str(e)}")
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in login request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during login: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)

    logger.warning(f"Invalid method {request.method} for login endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@csrf_exempt
@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL, block=True)
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Validate required fields
            if not email or not password:
                logger.warning(
                    f"Signup attempt with missing credentials: email={bool(email)}")
                return JsonResponse({
                    'error': 'Missing required fields: email and password',
                    'status': 'error'
                }, status=400)

            # Calculate the secret hash
            secret_hash = calculate_secret_hash(email)

            # Register user with Cognito
            cognito_client = get_cognito_client()
            response = cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                ]
            )

            logger.info(f"User signup successful: {email}")
            return JsonResponse({
                'message': 'Sign up successful! Please check your email to verify your account.',
                'status': 'success'
            }, status=201)

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                logger.warning(f"Signup failed: user already exists: {email}")
                return JsonResponse({
                    'error': 'User already exists',
                    'status': 'error'
                }, status=409)
            elif error_code == 'InvalidPasswordException':
                logger.warning(
                    f"Signup failed: invalid password for user: {email}")
                return JsonResponse({
                    'error': 'Password does not meet requirements',
                    'status': 'error'
                }, status=400)
            elif error_code == 'InvalidParameterException':
                logger.warning(
                    f"Signup failed: invalid parameter for user: {email}")
                return JsonResponse({
                    'error': 'Invalid parameter',
                    'status': 'error'
                }, status=400)
            else:
                logger.error(
                    f"Unexpected Cognito error during signup: {str(e)}")
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in signup request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during signup: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)

    logger.warning(f"Invalid method {request.method} for signup endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@csrf_exempt
def confirm_signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')

            if not email or not code:
                logger.warning(
                    f"Confirm signup attempt with missing fields: email={bool(email)}, code={bool(code)}")
                return JsonResponse({
                    'error': 'Missing required fields: email and code',
                    'status': 'error'
                }, status=400)

            secret_hash = calculate_secret_hash(email)

            cognito_client = get_cognito_client()
            cognito_client.confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=code
            )

            logger.info(f"User confirmed successfully: {email}")
            return JsonResponse({
                'message': 'Account confirmed! You can now log in.',
                'status': 'success'
            }, status=200)

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                logger.warning(f"Invalid confirmation code for user: {email}")
                return JsonResponse({
                    'error': 'Invalid confirmation code',
                    'status': 'error'
                }, status=400)
            elif error_code == 'ExpiredCodeException':
                logger.warning(f"Expired confirmation code for user: {email}")
                return JsonResponse({
                    'error': 'Confirmation code expired',
                    'status': 'error'
                }, status=400)
            elif error_code == 'UserNotFoundException':
                logger.warning(f"User not found during confirmation: {email}")
                return JsonResponse({
                    'error': 'User not found',
                    'status': 'error'
                }, status=404)
            elif error_code == 'NotAuthorizedException':
                logger.warning(f"User already confirmed: {email}")
                return JsonResponse({
                    'error': 'User already confirmed',
                    'status': 'error'
                }, status=400)
            else:
                logger.error(
                    f"Unexpected Cognito error during confirmation: {str(e)}")
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in confirm signup request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during confirm signup: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)

    logger.warning(
        f"Invalid method {request.method} for confirm-signup endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL, block=True)
def forgot_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                logger.warning(f"Forgot password attempt with missing email")
                return JsonResponse({
                    'error': 'Missing required field: email',
                    'status': 'error'
                }, status=400)

            # Calculate the secret hash
            secret_hash = calculate_secret_hash(email)

            # Initiate forgot password flow with Cognito
            cognito_client = get_cognito_client()
            cognito_client.forgot_password(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email
            )

            logger.info(f"Password reset initiated for user: {email}")
            return JsonResponse({
                'message': 'Password reset code sent to your email.',
                'status': 'success'
            }, status=200)

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                logger.warning(
                    f"Password reset attempted for non-existent user: {email}")
                return JsonResponse({
                    'error': 'User not found',
                    'status': 'error'
                }, status=404)
            elif error_code == 'LimitExceededException':
                logger.warning(
                    f"Password reset limit exceeded for user: {email}")
                return JsonResponse({
                    'error': 'Too many password reset attempts. Please try again later.',
                    'status': 'error'
                }, status=429)
            else:
                logger.error(
                    f"Unexpected Cognito error during password reset: {str(e)}")
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in forgot password request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during password reset: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)

    logger.warning(
        f"Invalid method {request.method} for forgot-password endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@csrf_exempt
def confirm_forgot_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            new_password = data.get('new_password')

            if not email or not code or not new_password:
                logger.warning(
                    f"Confirm forgot password attempt with missing fields: email={bool(email)}, code={bool(code)}, password={bool(new_password)}")
                return JsonResponse({
                    'error': 'Missing required fields: email, code, and new_password',
                    'status': 'error'
                }, status=400)

            # Calculate the secret hash
            secret_hash = calculate_secret_hash(email)

            # Confirm forgot password with Cognito
            cognito_client = get_cognito_client()
            cognito_client.confirm_forgot_password(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )

            logger.info(
                f"Password reset completed successfully for user: {email}")
            return JsonResponse({
                'message': 'Password reset successful! You can now log in with your new password.',
                'status': 'success'
            }, status=200)

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                logger.warning(f"Invalid reset code for user: {email}")
                return JsonResponse({
                    'error': 'Invalid reset code',
                    'status': 'error'
                }, status=400)
            elif error_code == 'ExpiredCodeException':
                logger.warning(f"Expired reset code for user: {email}")
                return JsonResponse({
                    'error': 'Reset code expired. Please request a new one.',
                    'status': 'error'
                }, status=400)
            elif error_code == 'UserNotFoundException':
                logger.warning(
                    f"User not found during password reset: {email}")
                return JsonResponse({
                    'error': 'User not found',
                    'status': 'error'
                }, status=404)
            elif error_code == 'InvalidPasswordException':
                logger.warning(f"Invalid new password for user: {email}")
                return JsonResponse({
                    'error': 'New password does not meet requirements',
                    'status': 'error'
                }, status=400)
            else:
                logger.error(
                    f"Unexpected Cognito error during password reset confirmation: {str(e)}")
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in confirm forgot password request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during password reset confirmation: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)

    logger.warning(
        f"Invalid method {request.method} for confirm-forgot-password endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@csrf_exempt
def verify_reset_code_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')

            if not email or not code:
                logger.warning(
                    f"Verify reset code attempt with missing fields: email={bool(email)}, code={bool(code)}")
                return JsonResponse({
                    'error': 'Missing required fields: email and code',
                    'status': 'error'
                }, status=400)

            secret_hash = calculate_secret_hash(email)

            # Use a password that passes Cognito's regex validation but fails password requirements
            # Regex requires: ^[\S]+.*[\S]+$ (at least 2 non-whitespace chars with something in between)
            # Password requirements: 8+ chars, uppercase, lowercase, number, special char
            invalid_password = 'ab'  # 2 chars, no uppercase, no number, no special char

            try:
                cognito_client = get_cognito_client()
                cognito_client.confirm_forgot_password(
                    ClientId=COGNITO_CLIENT_ID,
                    SecretHash=secret_hash,
                    Username=email,
                    ConfirmationCode=code,
                    Password=invalid_password
                )
                # If we reach here, something unexpected happened
                logger.error(
                    f"Unexpected success with invalid password for user: {email}")
                return JsonResponse({
                    'error': 'Verification failed - unexpected result',
                    'status': 'error'
                }, status=400)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'InvalidPasswordException':
                    # Code is valid, password is not - this is what we want
                    logger.info(
                        f"Reset code verified successfully for user: {email}")
                    return JsonResponse({
                        'message': 'Reset code is valid.',
                        'status': 'success'
                    }, status=200)
                elif error_code == 'CodeMismatchException':
                    logger.warning(f"Invalid reset code for user: {email}")
                    return JsonResponse({
                        'error': 'Invalid reset code',
                        'status': 'error'
                    }, status=400)
                elif error_code == 'ExpiredCodeException':
                    logger.warning(f"Expired reset code for user: {email}")
                    return JsonResponse({
                        'error': 'Reset code expired. Please request a new one.',
                        'status': 'error'
                    }, status=400)
                elif error_code == 'UserNotFoundException':
                    logger.warning(
                        f"User not found during reset code verification: {email}")
                    return JsonResponse({
                        'error': 'User not found',
                        'status': 'error'
                    }, status=404)
                elif error_code == 'LimitExceededException':
                    logger.warning(f"Too many attempts for user: {email}")
                    return JsonResponse({
                        'error': 'Too many verification attempts. Please try again later.',
                        'status': 'error'
                    }, status=429)
                else:
                    logger.error(
                        f"Unexpected Cognito error during reset code verification: {str(e)}")
                    return JsonResponse({
                        'error': 'An unexpected error occurred',
                        'status': 'error'
                    }, status=500)
            except Exception as e:
                logger.error(
                    f"Unexpected error during reset code verification: {str(e)}", exc_info=True)
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'status': 'error'
                }, status=500)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in verify reset code request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Unexpected error during verify reset code: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'status': 'error'
            }, status=500)
    logger.warning(
        f"Invalid method {request.method} for verify-reset-code endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@require_auth
def add_expense(request):
    """Add a new expense."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Get user_id from authenticated request
            user_id = request.user_info['user_id']

            # Extract expense data
            amount = data.get('amount')
            category = data.get('category')
            description = data.get('description', '')

            # Validate required fields
            if not all([amount, category]):
                logger.warning(
                    f"Add expense attempt with missing fields: amount={bool(amount)}, category={bool(category)}")
                return JsonResponse({
                    'error': 'Missing required fields: amount, category',
                    'status': 'error'
                }, status=400)

            # Validate amount is numeric
            try:
                float(amount)
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount format: {amount}")
                return JsonResponse({
                    'error': 'Amount must be a valid number',
                    'status': 'error'
                }, status=400)

            # Create expense using DynamoDB
            expense_db = DynamoDBExpenseService()
            expense = expense_db.create(user_id, amount, category, description)

            logger.info(
                f"Expense added successfully: user_id={user_id}, amount={amount}, category={category}")
            return JsonResponse({
                'message': 'Expense added successfully',
                'expense_id': expense['expense_id'],
                'expense': {
                    'id': expense['expense_id'],
                    'user_id': expense['user_id'],
                    'amount': str(expense['amount']),
                    'category': expense['category'],
                    'description': expense['description'],
                    'timestamp': expense['timestamp']
                },
                'status': 'success'
            }, status=201)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in add expense request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(f"Error adding expense: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An error occurred while adding expense',
                'status': 'error'
            }, status=500)

    logger.warning(f"Invalid method {request.method} for add expense endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@require_auth
def get_expenses(request):
    """Get expenses for a user."""
    if request.method == 'GET':
        try:
            # Get user_id from authenticated request
            user_id = request.user_info['user_id']

            # Get expenses using DynamoDB
            expense_db = DynamoDBExpenseService()
            expenses = expense_db.get_by_user(user_id)

            expense_list = []
            for expense in expenses:
                expense_list.append({
                    'id': expense['expense_id'],
                    'user_id': expense['user_id'],
                    'amount': str(expense['amount']),
                    'category': expense['category'],
                    'description': expense['description'],
                    'timestamp': expense['timestamp'],
                    'receipt_url': expense.get('receipt_url')
                })

            logger.info(
                f"Retrieved {len(expense_list)} expenses for user: {user_id}")
            return JsonResponse({
                'message': 'Expenses retrieved successfully',
                'expenses': expense_list,
                'count': len(expense_list),
                'status': 'success'
            })

        except Exception as e:
            logger.error(f"Error getting expenses: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An error occurred while retrieving expenses',
                'status': 'error'
            }, status=500)

    logger.warning(
        f"Invalid method {request.method} for get expenses endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@require_auth
def upload_receipt(request):
    """Upload a receipt file to S3."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Get user_id from authenticated request
            user_id = request.user_info['user_id']

            # Extract data
            file_data = data.get('file')
            file_name = data.get('filename')
            # Optional: link to existing expense
            expense_id = data.get('expense_id')

            # Validate required fields
            if not all([file_data, file_name]):
                logger.warning(
                    f"Receipt upload attempt with missing fields: file_data={bool(file_data)}, file_name={bool(file_name)}")
                return JsonResponse({
                    'error': 'Missing required fields: file, filename',
                    'status': 'error'
                }, status=400)

            # Validate file size (max 10MB)
            try:
                if file_data.startswith('data:'):
                    header, encoded = file_data.split(',', 1)
                    file_data = encoded

                file_bytes = base64.b64decode(file_data)
                if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
                    logger.warning(f"File too large: {len(file_bytes)} bytes")
                    return JsonResponse({
                        'error': 'File size exceeds 10MB limit',
                        'status': 'error'
                    }, status=400)
            except Exception as e:
                logger.error(f"Error processing file data: {str(e)}")
                return JsonResponse({
                    'error': 'Invalid file data format',
                    'status': 'error'
                }, status=400)

            # Upload to S3
            from utils.s3_utils import S3Handler
            s3_handler = S3Handler()

            # Check if bucket exists
            if not s3_handler.check_bucket_exists():
                logger.error(
                    f"S3 bucket {s3_handler.bucket_name} does not exist")
                return JsonResponse({
                    'error': 'Storage service not available',
                    'status': 'error'
                }, status=503)

            # Upload file
            upload_result = s3_handler.upload_file(
                file_data, file_name, user_id)

            if not upload_result['success']:
                logger.error(f"S3 upload failed: {upload_result.get('error')}")
                return JsonResponse({
                    'error': 'Failed to upload file',
                    'status': 'error'
                }, status=500)

            # If expense_id provided, update the expense with receipt URL
            if expense_id:
                expense_db = DynamoDBExpenseService()
                expense_db.update_receipt_url(
                    expense_id, upload_result['file_url'])
                logger.info(f"Receipt URL updated for expense: {expense_id}")

            logger.info(
                f"Receipt uploaded successfully: {upload_result['file_key']} for user {user_id}")

            return JsonResponse({
                'message': 'Receipt uploaded successfully',
                'file_url': upload_result['file_url'],
                'file_key': upload_result['file_key'],
                'file_name': upload_result['file_name'],
                'expense_id': expense_id,
                'status': 'success'
            }, status=201)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in receipt upload request")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        except Exception as e:
            logger.error(f"Error uploading receipt: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'An error occurred while uploading receipt',
                'status': 'error'
            }, status=500)

    logger.warning(
        f"Invalid method {request.method} for upload receipt endpoint")
    return JsonResponse({
        'error': 'Method not allowed',
        'status': 'error'
    }, status=405)


@require_auth
@require_http_methods(["GET", "PUT"])
def profile_view(request):
    if request.method == 'GET':
        try:
            # The user_info is attached by the JWTAuthenticationMiddleware
            return JsonResponse({'profile': request.user_info, 'status': 'success'})
        except Exception as e:
            logger.error(f"Unexpected error in get_profile_view: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred', 'status': 'error'}, status=500)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name')
            if not email and not name:
                return JsonResponse({'error': 'No fields to update', 'status': 'error'}, status=400)
            cognito_client = get_cognito_client()
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                return JsonResponse({'error': 'Authentication token missing', 'status': 'error'}, status=401)

            user_attributes = []
            if email:
                user_attributes.append({'Name': 'email', 'Value': email})
            if name:
                user_attributes.append({'Name': 'name', 'Value': name})
            cognito_client.update_user_attributes(
                AccessToken=access_token,
                UserAttributes=user_attributes
            )
            return JsonResponse({'message': 'Profile updated successfully', 'status': 'success'})
        except ClientError as e:
            logger.error(f"Cognito error in update_profile_view: {str(e)}")
            return JsonResponse({'error': 'Failed to update profile', 'status': 'error'}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error in update_profile_view: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred', 'status': 'error'}, status=500)


@require_auth
@require_POST
def change_password_view(request):
    """Change the user's password in Cognito (requires current and new password)."""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not current_password or not new_password:
            return JsonResponse({'error': 'Missing required fields: current_password and new_password', 'status': 'error'}, status=400)
        cognito_client = get_cognito_client()
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Authentication token missing', 'status': 'error'}, status=401)

        cognito_client.change_password(
            PreviousPassword=current_password,
            ProposedPassword=new_password,
            AccessToken=access_token
        )
        return JsonResponse({'message': 'Password changed successfully', 'status': 'success'})
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            return JsonResponse({'error': 'Current password is incorrect', 'status': 'error'}, status=401)
        elif error_code == 'InvalidPasswordException':
            return JsonResponse({'error': 'New password does not meet requirements', 'status': 'error'}, status=400)
        logger.error(f"Cognito error in change_password_view: {str(e)}")
        return JsonResponse({'error': 'Failed to change password', 'status': 'error'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in change_password_view: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred', 'status': 'error'}, status=500)


def healthz(request):
    return JsonResponse({"status": "ok"})


@require_http_methods(["PUT"])
@require_auth
def update_expense(request, expense_id):
    """
    Update an existing expense.

    Expected JSON payload (all fields are optional except amount which is required if provided):
    {
        "amount": 100.50,
        "category": "Food",
        "description": "Dinner with team"
    }
    """
    try:
        # Get the user ID from the request (set by JWTAuthenticationMiddleware)
        user_id = request.user_info['user_id']

        # Parse request data
        data = json.loads(request.body)

        # Validate that at least one field is being updated
        if not any(key in data for key in ['amount', 'category', 'description']):
            return JsonResponse({
                'error': 'At least one field (amount, category, or description) is required',
                'status': 'error'
            }, status=400)

        # Validate amount if provided
        if 'amount' in data:
            try:
                # Convert to float if it's a string, or keep as is if it's already a number
                amount = float(data['amount']) if isinstance(
                    data['amount'], str) else data['amount']

                # Check if the converted value is a valid positive number
                if not isinstance(amount, (int, float)) or amount <= 0:
                    raise ValueError("Amount must be a positive number")

                # Update the data with the converted amount
                data['amount'] = amount

            except (ValueError, TypeError) as e:
                return JsonResponse({
                    'error': 'Amount must be a positive number',
                    'status': 'error'
                }, status=400)

        # Update the expense
        expense_service = DynamoDBExpenseService()
        updated_expense = expense_service.update_expense(
            expense_id=expense_id,
            user_id=user_id,
            amount=data.get('amount'),
            category=data.get('category'),
            description=data.get('description')
        )

        if not updated_expense:
            return JsonResponse({
                'error': 'Expense not found or you do not have permission to update it',
                'status': 'error'
            }, status=404)

        return JsonResponse({
            'message': 'Expense updated successfully',
            'expense': updated_expense,
            'status': 'success'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON payload',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating expense: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while updating the expense',
            'status': 'error'
        }, status=500)


@require_http_methods(["DELETE"])
@require_auth
def delete_expense(request, expense_id):
    """
    Delete an expense.
    """
    try:
        # Get the user ID from the request (set by JWTAuthenticationMiddleware)
        user_id = request.user_info['user_id']

        # Delete the expense
        expense_service = DynamoDBExpenseService()
        success = expense_service.delete_expense(expense_id, user_id)

        if not success:
            return JsonResponse({
                'error': 'Expense not found or you do not have permission to delete it',
                'status': 'error'
            }, status=404)

        return JsonResponse({
            'message': 'Expense deleted successfully',
            'status': 'success'
        })

    except Exception as e:
        logger.error(f"Error deleting expense: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while deleting the expense',
            'status': 'error'
        }, status=500)
