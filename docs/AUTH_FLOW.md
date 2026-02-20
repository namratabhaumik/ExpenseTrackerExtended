# Authentication Flows

Detailed documentation of authentication mechanisms in both local and cloud modes.

## Login Flow

### Local Mode (Django Sessions)

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
    ├─ Create Django User if needed
    ├─ Authenticate with Django auth
    ├─ Create session via login()
    │
    ↓
Django SessionBackend
    ├─ Create session in database
    ├─ Generate session key
    ├─ Return session data
    │
    ↓
Backend Response
    ├─ Set sessionid cookie:
    │  ├─ value = session_key (32-char random)
    │  ├─ httponly = True
    │  ├─ secure = False (local dev)
    │  ├─ samesite = Lax
    │  └─ max_age = 1209600 (14 days)
    │
    ├─ Return JSON:
    │  {
    │    "status": "success",
    │    "email": "demo@test.com",
    │    "csrf_token": "xyz123..."
    │  }
    │
    ↓
Frontend
    ├─ Store csrf_token in memory (clearable)
    ├─ Receive sessionid cookie (automatic)
    ├─ Redirect to dashboard
    │
    ↓
Authenticated
    └─ Ready for API calls with session cookie
```

### Cloud Mode (AWS Cognito)

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
    ├─ Call AWS Cognito initiate_auth()
    │
    ↓
AWS Cognito
    ├─ Verify credentials in user pool
    ├─ Generate JWT tokens:
    │  ├─ id_token (contains user claims)
    │  ├─ access_token (for API access)
    │  └─ refresh_token (for token refresh)
    │
    ↓
Backend Response
    ├─ Set access_token cookie:
    │  ├─ httponly = True
    │  ├─ secure = True (HTTPS only)
    │  ├─ samesite = None
    │  └─ max_age = 3600 (1 hour)
    │
    ├─ Return JSON:
    │  {
    │    "status": "success",
    │    "email": "user@example.com",
    │    "id_token": "cognito_id_token",
    │    "csrf_token": "xyz123..."
    │  }
    │
    ↓
Frontend
    ├─ Store refresh_token in localStorage
    ├─ Receive access_token cookie
    ├─ Redirect to dashboard
    │
    ↓
Authenticated
    └─ Ready for API calls with Cognito tokens
```

## Signup Flow

### Local Mode (Django Session)

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
    ├─ Create Django User
    ├─ Hash password with Django's password hasher
    ├─ Save to database
    ├─ User auto-confirmed in local mode
    │
    ↓
Response
    {
        "status": "success",
        "message": "Sign up successful! You can now log in."
    }
    │
    ↓
Frontend
    ├─ Show success message
    ├─ Redirect to login
    │
    ↓
Ready to Login
    └─ User can now login with new credentials
```

### Cloud Mode (AWS Cognito)

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
        "status": "success",
        "message": "Sign up successful! Check your email for confirmation code."
    }
    │
    ↓
Frontend
    ├─ Show success message
    ├─ Prompt for email verification code
    │
    ↓
Awaiting Email Confirmation
    └─ User must verify email before login
```

## Request Authentication

### Local Mode (Django Session)

```
Client sends request to protected endpoint
    │
    ├─ Cookies: sessionid=xyz123...
    ├─ Headers: X-CSRFToken: csrf_token_value
    │
    ↓
Django SessionMiddleware
    ├─ Extract sessionid from cookie
    ├─ Look up session in database
    ├─ Load session data
    │
    ↓
Django CsrfViewMiddleware
    ├─ Extract X-CSRFToken header
    ├─ Compare with CSRF token in session
    ├─ Verify they match
    │
    ↓
View Function
    ├─ request.user is authenticated
    ├─ request.user.email contains user email
    ├─ Process request
    │
    ↓
Response
    └─ Return data for authenticated user
```

### Cloud Mode (Cognito)

```
Client sends request to protected endpoint
    │
    ├─ Headers: Authorization: Bearer access_token
    │  OR
    ├─ Cookies: access_token=cognito_token
    │
    ↓
Backend Auth Handler
    ├─ Extract token from header or cookie
    ├─ Call Cognito get_user()
    ├─ Validate token signature
    ├─ Check expiration
    ├─ Get user attributes
    │
    ↓
View Function
    ├─ request.user_info contains user data
    ├─ request.user_info['email'] = user email
    ├─ Process request
    │
    ↓
Response
    └─ Return data for authenticated user
```

## CSRF Protection (Local Mode)

```
1. Get CSRF Token
    ↓
    GET /api/csrf-token/
    ↓
    Django sets csrftoken cookie
    ↓
    Frontend reads cookie via JavaScript

2. Use CSRF Token
    ↓
    POST /api/login/
    {
        "email": "test@example.com",
        "password": "password"
    }
    Headers: X-CSRFToken: value_from_cookie
    ↓
    Django validates token matches

3. Token Rotation
    ↓
    After login, CSRF token is cleared
    ↓
    Frontend must fetch new token
    ↓
    GET /api/csrf-token/ again
```

## Session Persistence (Local Mode)

Sessions are stored in Django's session database:
- **Location**: `django_session` table in SQLite
- **Duration**: 14 days (configurable)
- **Auto-cleanup**: Django cleans expired sessions periodically

Session data structure:
```json
{
  "session_key": "32_character_random_string",
  "session_data": "encoded_session_dict",
  "expire_date": "2026-03-05 19:52:00"
}
```

## Logout Flow

```
User clicks Logout button
    │
    ↓
Frontend
    ├─ Clear stored CSRF token
    ├─ Clear localStorage/sessionStorage
    ├─ POST /api/logout/
    │
    ↓
Backend
    ├─ [LOCAL MODE]                 vs.    [CLOUD MODE]
    │
    ├─ Call Django logout()             ├─ Call Cognito admin_user_global_sign_out()
    │  (deletes session)                ├─ Invalidate all tokens
    │
    ↓                                     ↓
    │
Response
    {
        "status": "success",
        "message": "Logged out successfully"
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
[Local Mode]                [Cloud Mode]
├─ Check Django user       ├─ Cognito returns
├─ Verify password hash    │  NotAuthorizedException
├─ Return 401 error        ├─ Backend returns 401
├─ Message: "Invalid       └─ Frontend shows
│  credentials"              error message

Missing Session/Token
    ↓
Frontend sends request without authentication
    │
    ↓
[Local Mode]                [Cloud Mode]
├─ No sessionid cookie     ├─ No bearer token
├─ Return 401              ├─ Return 401
    │
    ↓
Frontend
    ├─ Redirect to login
    ├─ Clear stored auth data

Expired Session/Token
    ↓
[Local Mode]                [Cloud Mode]
├─ Session expired         ├─ Token expired
├─ Return 401              ├─ Frontend uses refresh_token
├─ User must re-login      ├─ If refresh fails, redirect to login
```

## Password Change

```
User changes password (Profile > Change Password)
    │
    ↓
POST /api/change-password/
    {
        "current_password": "old_pass",
        "new_password": "new_pass"
    }
    │
    ↓
Backend
    ├─ Verify current password
    ├─ Update password in database
    ├─ [LOCAL MODE ONLY] Force logout:
    │  ├─ Delete current session
    │  ├─ Return 401 response
    │
    ↓
Frontend
    ├─ Receives 401 response
    ├─ Auto-logout happens
    ├─ Clear CSRF token
    ├─ Redirect to login page
    ├─ Show "Password changed, please login again"
    │
    ↓
User must login with new password
```
