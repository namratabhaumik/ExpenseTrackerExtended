"""
Test settings for expense_tracker project.
This file overrides production settings to avoid external dependencies during testing.
"""

import os
import sys
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Override SECRET_KEY for testing
SECRET_KEY = 'test-secret-key-for-testing-only'

# Override DEBUG for testing
DEBUG = True

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Override AWS configuration for testing
AWS_ACCESS_KEY_ID = 'test-access-key'
AWS_SECRET_ACCESS_KEY = 'test-secret-key'
AWS_REGION = 'us-east-1'

# Override DynamoDB configuration for testing
DYNAMODB_TABLE_NAME = 'test-expenses-table'
DYNAMODB_ENDPOINT_URL = None

# Override Cognito configuration for testing
COGNITO_USER_POOL_ID = 'test-user-pool-id'
COGNITO_CLIENT_ID = 'testclientid123'
COGNITO_CLIENT_SECRET = 'test-client-secret'

# Override S3 configuration for testing
S3_BUCKET_NAME = 'test-bucket'
S3_REGION = 'us-east-1'

# Use in-memory cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-expense-tracker-test"
    }
}

# Silence django-ratelimit warnings for testing
SILENCED_SYSTEM_CHECKS = [
    "django_ratelimit.E003",
    "django_ratelimit.W001",
]

# Override logging for testing to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'auth_app': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
