import boto3
import json
import hmac
import hashlib
import base64
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

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

        except cognito_client.exceptions.NotAuthorizedException:
            logger.warning(f"Invalid credentials for user: {email}")
            return JsonResponse({
                'error': 'Invalid credentials',
                'status': 'error'
            }, status=401)
        except cognito_client.exceptions.UserNotFoundException:
            logger.warning(f"User not found: {email}")
            return JsonResponse({
                'error': 'User does not exist',
                'status': 'error'
            }, status=404)
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
def add_expense(request):
    """Add a new expense."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract expense data
            user_id = data.get('user_id')
            amount = data.get('amount')
            category = data.get('category')
            description = data.get('description', '')

            # Validate required fields
            if not all([user_id, amount, category]):
                logger.warning(
                    f"Add expense attempt with missing fields: user_id={bool(user_id)}, amount={bool(amount)}, category={bool(category)}")
                return JsonResponse({
                    'error': 'Missing required fields: user_id, amount, category',
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


@csrf_exempt
def get_expenses(request):
    """Get expenses for a user."""
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')

            if not user_id:
                logger.warning(
                    "Get expenses attempt without user_id parameter")
                return JsonResponse({
                    'error': 'user_id parameter is required',
                    'status': 'error'
                }, status=400)

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


@csrf_exempt
def upload_receipt(request):
    """Upload a receipt file."""
    if request.method == 'POST':
        try:
            # For now, we'll just return a success message
            # TODO: Implement actual file upload to S3
            logger.info("Receipt upload endpoint called (not yet implemented)")
            return JsonResponse({
                'message': 'Receipt upload endpoint - S3 integration pending',
                'status': 'not_implemented'
            }, status=501)

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
