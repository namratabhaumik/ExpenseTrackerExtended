"""
Local development settings for expense_tracker.

Used for local development with SQLite, local authentication, and local file storage.
"""

from .base import *

# Add local app for local development implementations
INSTALLED_APPS.append('local_app')

# DEBUG mode for development
DEBUG = True

# Database Configuration - SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Caching configuration - In-memory cache for local development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-expense-tracker"
    }
}

# Silence django-ratelimit warnings about non-shared cache
# Using LocMemCache is acceptable for local development
SILENCED_SYSTEM_CHECKS = [
    "django_ratelimit.E003",
    "django_ratelimit.W001",
]

# Local authentication - uses local implementations
# These are set for compatibility with code that may check these settings
# In the future, configuration can be removed when code is fully refactored
IS_LOCAL_DEMO = True
