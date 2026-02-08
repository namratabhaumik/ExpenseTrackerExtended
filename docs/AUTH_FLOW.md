# Authentication Flows

Detailed documentation of authentication mechanisms in both local and cloud modes.

## Login Flow

### Local Mode

```
User (Frontend)
    │
    ├─ Email: demo@test.com
    ├─ Password: anypassword
    │
    ↓
Frontend Validation
    ├─ Check email format
    ├─ Check password length
    │
    ↓
POST /api/login/
    {
        "email": "demo@test.com",
        "password": "anypassword"
    }
    │
    ↓
Backend (views.py - login_view)
    ├─ IS_LOCAL_DEMO = true
    ├─ Call local_auth.local_login()
    │
    ↓
local_auth.py
    ├─ Accept any credentials
    ├─ Create mock user_id: "demo_test_com"
    ├─ Create JWT payload:
    │  {
    │    "sub": "demo@test.com",
    │    "iat": 1707417600,
    │    "exp": 1707504000
    │  }
    ├─ Encode as base64
    │
    ↓
Backend Response
    ├─ Set HttpOnly cookie:
    │  ├─ access_token = base64(payload)
    │  ├─ httponly = True
    │  ├─ secure = False (local)
    │  ├─ samesite = Lax
    │  └─ max_age = 86400 (24 hours)
    │
    ├─ Return JSON:
    │  {
    │    "message": "Login successful",
    │    "id_token": "...",
    │    "refresh_token": "...",
    │    "status": "success"
    │  }
    │
    ↓
Frontend
    ├─ Store refresh_token in localStorage
    ├─ Receive access_token in cookie (automatic)
    ├─ Redirect to dashboard
    │
    ↓
Authenticated
    └─ Ready for API calls with access_token cookie
```

### Cloud Mode

```
User (Frontend)
    │
    ├─ Email: user@example.com
    ├─ Password: SecurePassword123!
    │
    ↓
Frontend Validation
    ├─ Check email format
    ├─ Check password complexity
    │
    ↓
POST /api/login/
    {
        "email": "user@example.com",
        "password": "SecurePassword123!"
    }
    │
    ↓
Backend (views.py - login_view)
    ├─ IS_LOCAL_DEMO = false
    ├─ Calculate secret_hash (HMAC-SHA256)
    ├─ Call AWS Cognito
    │
    ↓
AWS Cognito
    ├─ initiate_auth() with:
    │  ├─ AuthFlow: USER_PASSWORD_AUTH
    │  ├─ ClientId: COGNITO_CLIENT_ID
    │  ├─ Username: user@example.com
    │  ├─ Password: SecurePassword123!
    │  └─ SECRET_HASH: calculated_hash
    │
    ├─ Verify credentials in user pool
    ├─ Generate JWT tokens:
    │  ├─ id_token (contains user claims)
    │  ├─ access_token (for API access)
    │  └─ refresh_token (for token refresh)
    │
    ↓
Backend Response
    ├─ Set HttpOnly cookie:
    │  ├─ access_token = Cognito_AccessToken
    │  ├─ httponly = True
    │  ├─ secure = True (HTTPS only)
    │  ├─ samesite = None
    │  └─ max_age = 3600 (1 hour)
    │
    ├─ Return JSON:
    │  {
    │    "message": "Login successful",
    │    "id_token": "cognito_id_token",
    │    "refresh_token": "cognito_refresh_token",
    │    "status": "success"
    │  }
    │
    ↓
Frontend
    ├─ Store refresh_token in localStorage
    ├─ Receive access_token in cookie
    ├─ Redirect to dashboard
    │
    ↓
Authenticated
    └─ Ready for API calls with Cognito tokens
```

## Signup Flow

### Local Mode

```
User (Frontend)
    │
    ├─ Email: newuser@test.com
    ├─ Password: password123
    │
    ↓
Frontend Validation
    ├─ Check email format
    ├─ Check password requirements
    │
    ↓
POST /api/signup/
    {
        "email": "newuser@test.com",
        "password": "password123"
    }
    │
    ↓
Backend (signup_view)
    ├─ IS_LOCAL_DEMO = true
    ├─ Call local_auth.local_signup()
    ├─ Validate email format
    ├─ Accept signup
    │
    ↓
Response
    {
        "message": "Sign up successful! You can now log in.",
        "status": "success"
    }
    │
    ↓
Frontend
    ├─ Show success message
    ├─ Redirect to login
    │
    ↓
Ready to Login
```

### Cloud Mode

```
User (Frontend)
    │
    ├─ Email: newuser@example.com
    ├─ Password: SecurePassword123!
    │
    ↓
Frontend Validation
    ├─ Check email format
    ├─ Check password complexity
    │  └─ At least 8 chars, uppercase, lowercase, number, special char
    │
    ↓
POST /api/signup/
    {
        "email": "newuser@example.com",
        "password": "SecurePassword123!"
    }
    │
    ↓
Backend (signup_view)
    ├─ IS_LOCAL_DEMO = false
    ├─ Calculate secret_hash
    ├─ Call AWS Cognito sign_up()
    │
    ↓
AWS Cognito
    ├─ Create new user in user pool
    ├─ Send confirmation email with code
    ├─ Return response (requires email confirmation)
    │
    ↓
Backend Response
    {
        "message": "Sign up successful! Check your email for confirmation code.",
        "status": "success"
    }
    │
    ↓
Frontend
    ├─ Show success message
    ├─ Prompt for email verification code
    │
    ↓
Awaiting Email Confirmation
```

## Token Validation

### On Protected API Calls

```
Client sends request to protected endpoint
    │
    ├─ Headers: Authorization: Bearer token
    │  OR
    ├─ Cookies: access_token=...
    │
    ↓
Middleware (JWTAuthenticationMiddleware)
    ├─ Extract token from header or cookie
    │
    ├─ [LOCAL MODE]                  vs.    [CLOUD MODE]
    │
    ├─ Decode base64                      ├─ Call Cognito get_user()
    ├─ Verify JWT structure              ├─ Validate token signature
    ├─ Extract user_email                ├─ Check expiration
    │                                     ├─ Get user attributes
    │
    ↓                                       ↓
    │
    Set request.user_info = {
        'user_id': 'email_based_id',
        'email': 'user@example.com',
        'name': 'user'
    }
    │
    ↓
View Function
    ├─ Access request.user_info
    ├─ Verify user owns requested resource
    ├─ Process request
    │
    ↓
Response
    └─ Return data for authenticated user
```

## Token Refresh

### Local Mode

```
Access Token Expired (24 hours)
    │
    ↓
Frontend checks response status
    ├─ If 401 Unauthorized
    ├─ Use refresh_token from localStorage
    │
    ↓
POST /api/refresh-token/
    {
        "refresh_token": "stored_refresh_token"
    }
    │
    ↓
Backend
    ├─ IS_LOCAL_DEMO = true
    ├─ Decode refresh_token
    ├─ Validate expiration
    ├─ Generate new access_token
    │
    ↓
Response
    {
        "access_token": "new_access_token"
    }
    │
    ↓
Frontend
    ├─ Update cookie with new access_token
    ├─ Retry original request
    │
    ↓
Request Succeeds
```

### Cloud Mode

```
Access Token Expired (1 hour)
    │
    ↓
Frontend checks response status
    ├─ If 401 Unauthorized
    ├─ Use refresh_token from localStorage
    │
    ↓
POST /api/refresh-token/
    {
        "refresh_token": "cognito_refresh_token"
    }
    │
    ↓
Backend
    ├─ IS_LOCAL_DEMO = false
    ├─ Call Cognito initiate_auth()
    ├─ AuthFlow: REFRESH_TOKEN_AUTH
    ├─ Use refresh_token
    │
    ↓
AWS Cognito
    ├─ Validate refresh_token
    ├─ Issue new access_token and id_token
    │
    ↓
Backend
    ├─ Set new access_token in cookie
    ├─ Return new tokens
    │
    ↓
Frontend
    ├─ Update stored tokens
    ├─ Retry original request
    │
    ↓
Request Succeeds
```

## Logout Flow

```
User clicks Logout button
    │
    ↓
Frontend
    ├─ Clear localStorage (refresh_token)
    ├─ Clear cookies
    ├─ POST /api/logout/
    │
    ↓
Backend
    ├─ Clear session (if used)
    │
    ├─ [LOCAL MODE]           vs.    [CLOUD MODE]
    │
    ├─ Nothing to invalidate         ├─ Call Cognito admin_user_global_sign_out()
    │  (tokens expire anyway)        ├─ Invalidate all tokens
    │
    ↓                                  ↓
    │
Response
    {
        "message": "Logged out successfully",
        "status": "success"
    }
    │
    ↓
Frontend
    ├─ Redirect to login page
    ├─ Clear app state
    │
    ↓
Logged Out
    └─ User must login again
```

## Error Handling

### Authentication Errors

```
Invalid Credentials
    ↓
[Local Mode]              [Cloud Mode]
├─ Always accept         ├─ Cognito returns
├─ Return tokens         │  NotAuthorizedException
                         ├─ Backend returns 401
                         └─ Frontend shows error message

Missing Token
    ↓
Frontend sends request without token
    │
    ↓
Middleware checks
    │
    ├─ No token found
    │
    ↓
Return 401 Unauthorized
    │
    ↓
Frontend
    ├─ Redirect to login
    ├─ Clear stored auth data

Expired Token
    ↓
Token.exp < current_time
    │
    ↓
Middleware rejects
    │
    ↓
Return 401 Unauthorized
    │
    ↓
Frontend
    ├─ Try to refresh with refresh_token
    ├─ If refresh fails, redirect to login
```

