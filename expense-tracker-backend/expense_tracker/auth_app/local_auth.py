"""
Local/Demo Authentication Module
Uses mock authentication for local development without AWS Cognito.
"""
import base64
import json
from datetime import datetime

# Store for local users (in-memory for demo purposes)
LOCAL_USERS_DB = {}


def create_mock_tokens(email):
    """Create mock JWT tokens for local development."""
    # Create a simple mock token (not a real JWT, just for demo)
    payload = {
        'sub': email,
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int(datetime.utcnow().timestamp()) + 86400  # 24 hours
    }

    # Simple base64 encoding (NOT secure, for demo only)
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    return token


def local_login(email, password):
    """
    Mock login for local development.
    Accepts any email/password combination and logs them in.
    """
    if not email or not password:
        return None, "Missing email or password"

    # In local mode, accept any credentials
    # Store the user for future reference
    user_id = email.replace('@', '_').replace('.', '_')

    id_token = create_mock_tokens(email)
    access_token = create_mock_tokens(email)
    refresh_token = create_mock_tokens(email)

    return {
        'id_token': id_token,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user_id,
    }, None


def local_signup(email, password):
    """
    Mock signup for local development.
    Auto-confirms users immediately.
    """
    if not email or not password:
        return False, "Missing email or password"

    if not email.endswith('@') and '@' in email:
        # Just check it looks like an email
        return True, "Signup successful"

    return False, "Invalid email format"


def verify_local_token(token):
    """
    Verify mock token for local development.
    Just decodes the base64 mock token.
    """
    try:
        if not token:
            return None

        payload = json.loads(base64.b64decode(token).decode())
        return payload.get('sub')  # Return the email/user_id
    except Exception:
        return None
