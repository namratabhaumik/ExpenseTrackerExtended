import boto3
import json
import hmac
import hashlib
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

# Try to load .env file directly in this module
try:
    from dotenv import load_dotenv
    env_file_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_file_path)
    print(f"[DEBUG] dotenv imported and .env loaded from: {env_file_path}")
except ImportError as e:
    print(f"[DEBUG] Failed to import dotenv: {e}")
except Exception as e:
    print(f"[DEBUG] Failed to load .env: {e}")

# Cognito configuration
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.environ.get('COGNITO_CLIENT_SECRET')

print(f"[DEBUG] COGNITO_REGION: {COGNITO_REGION}")
print(f"[DEBUG] COGNITO_CLIENT_ID: {COGNITO_CLIENT_ID}")
print(f"[DEBUG] COGNITO_CLIENT_SECRET: {COGNITO_CLIENT_SECRET}")

# Debug: Check if .env file exists
env_file_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))), '.env')
print(f"[DEBUG] .env file path: {env_file_path}")
print(f"[DEBUG] .env file exists: {os.path.exists(env_file_path)}")

# Debug: Try to read .env file contents directly
try:
    with open(env_file_path, 'r') as f:
        env_contents = f.read()
        print(
            f"[DEBUG] .env file contents (first 100 chars): {env_contents[:100]}...")
except Exception as e:
    print(f"[DEBUG] Failed to read .env file: {e}")

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
