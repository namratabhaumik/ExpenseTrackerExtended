import boto3
import json
import hmac
import hashlib
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

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

            # Calculate the secret hash
            secret_hash = calculate_secret_hash(email)

            # Authenticate user with Cognito
            response = cognito_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                ClientId=COGNITO_CLIENT_ID,
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash,  # Add the secret hash here
                }
            )

            # If successful, return the tokens
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']

            return JsonResponse({
                'message': 'Login successful',
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': refresh_token,
            })

        except cognito_client.exceptions.NotAuthorizedException:
            return JsonResponse({'message': 'Invalid credentials'}, status=400)
        except cognito_client.exceptions.UserNotFoundException:
            return JsonResponse({'message': 'User does not exist'}, status=404)
        except Exception as e:
            print(f"Error during Cognito authentication: {e}")
            return JsonResponse({'message': 'An error occurred'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


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
                return JsonResponse({
                    'message': 'Missing required fields: user_id, amount, category'
                }, status=400)

            # Create expense using DynamoDB
            from .models import DynamoDBExpense
            expense_db = DynamoDBExpense()
            expense = expense_db.create(user_id, amount, category, description)

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
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error adding expense: {e}")
            return JsonResponse({'message': 'An error occurred'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def get_expenses(request):
    """Get expenses for a user."""
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')

            if not user_id:
                return JsonResponse({
                    'message': 'user_id parameter is required'
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

            return JsonResponse({
                'message': 'Expenses retrieved successfully',
                'expenses': expense_list,
                'count': len(expense_list)
            })

        except Exception as e:
            print(f"Error getting expenses: {e}")
            return JsonResponse({'message': 'An error occurred'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def upload_receipt(request):
    """Upload a receipt file."""
    if request.method == 'POST':
        try:
            # For now, we'll just return a success message
            # TODO: Implement actual file upload to S3
            return JsonResponse({
                'message': 'Receipt upload endpoint - S3 integration pending',
                'status': 'not_implemented'
            }, status=501)

        except Exception as e:
            print(f"Error uploading receipt: {e}")
            return JsonResponse({'message': 'An error occurred'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)
