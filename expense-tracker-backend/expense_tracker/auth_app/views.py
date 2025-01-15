import boto3
import json
import hmac
import hashlib
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Cognito configuration
COGNITO_REGION = 'us-east-1'
COGNITO_CLIENT_ID = '7p5c71fj183ut48sh0o6smqais'
COGNITO_CLIENT_SECRET = '10li562ia72k7spdfc9cn45u28r6uk4fdl9mtmj4fvu7a4m2su4o'

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
