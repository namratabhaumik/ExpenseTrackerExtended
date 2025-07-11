import boto3
import json
import hmac
import hashlib
import base64
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .middleware import require_auth
from botocore.exceptions import ClientError

# Get logger for this module
logger = logging.getLogger(__name__)

# Load .env file for environment variables
try:
    from dotenv import load_dotenv
    env_file_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_file_path)
except ImportError:
    pass  # dotenv not available, continue without it

# Cognito configuration
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.environ.get('COGNITO_CLIENT_SECRET')

# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)


def calculate_secret_hash(username):
    """Generate the SECRET_HASH for Cognito."""
    message = username + COGNITO_CLIENT_ID
    secret = bytes(COGNITO_CLIENT_SECRET, 'utf-8')
    digest = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


@csrf_exempt
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
            return JsonResponse({
                'message': 'Login successful',
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': refresh_token,
                'status': 'success'
            })

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
            from .models import DynamoDBExpense
            expense_db = DynamoDBExpense()
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
            from .models import DynamoDBExpense
            expense_db = DynamoDBExpense()
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
                from .models import DynamoDBExpense
                expense_db = DynamoDBExpense()
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


def healthz(request):
    return JsonResponse({"status": "ok"})
