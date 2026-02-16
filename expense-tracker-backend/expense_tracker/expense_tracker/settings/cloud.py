"""
Cloud deployment settings for expense_tracker.

Used for cloud deployment on Google Cloud Run with cloud resources:
- DynamoDB for data persistence
- Cognito for user authentication
- S3 for file storage
"""

import os

import dj_database_url

from .base import INSTALLED_APPS, MIDDLEWARE as BASE_MIDDLEWARE, TEMPLATES as BASE_TEMPLATES

# Ensure base MIDDLEWARE/TEMPLATES are present in this settings module
MIDDLEWARE = BASE_MIDDLEWARE
TEMPLATES = BASE_TEMPLATES

# Add cloud app for cloud deployment implementations
INSTALLED_APPS.append('cloud_app')

# Import after adding cloud_app to INSTALLED_APPS
from cloud_app.implementations.utils.gcp_secrets import get_secret  # noqa: E402

# DEBUG mode disabled for production
DEBUG = False

# Production-specific security settings
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# Trust the frontend origin for CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://expense-tracker-frontend-1a909.web.app',
    'https://expense-tracker-frontend-1a909.firebaseapp.com',
]

# Secret key from Google Secret Manager
SECRET_KEY = get_secret('DJANGO_SECRET_KEY')

# Database Configuration
# Priority: DATABASE_URL (for Cloud SQL) > PostgreSQL fallback
if 'DATABASE_URL' in os.environ:
    # Use the database defined by DATABASE_URL (Cloud SQL)
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback for other cloud PostgreSQL environments
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
        }
    }

# AWS Configuration
AWS_ACCESS_KEY_ID = get_secret('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# DynamoDB Configuration
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'expense-tracker-table')
DYNAMODB_ENDPOINT_URL = os.environ.get('DYNAMODB_ENDPOINT_URL', None)

# Cognito Configuration
COGNITO_USER_POOL_ID = get_secret('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = get_secret('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = get_secret('COGNITO_CLIENT_SECRET')

# S3 Configuration
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'expense-tracker-receipts')
S3_REGION = os.environ.get('S3_REGION', AWS_REGION)

# Caching configuration - In-memory cache for Cloud Run
# Acceptable for single-instance deployments which is typical for Cloud Run
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-expense-tracker"
    }
}

# Silence django-ratelimit warnings about non-shared cache
# Using LocMemCache is acceptable because Cloud Run typically runs single instances
SILENCED_SYSTEM_CHECKS = [
    "django_ratelimit.E003",
    "django_ratelimit.W001",
]

# Cloud authentication - uses cloud implementations
IS_LOCAL_DEMO = False
