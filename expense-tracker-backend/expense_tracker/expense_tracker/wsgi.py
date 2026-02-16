"""
WSGI config for expense_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting WSGI application...")

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger.info("Environment variables loaded")

# Default to local settings; can be overridden by DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.local')
logger.info(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

logger.info("Getting WSGI application...")
application = get_wsgi_application()
logger.info("WSGI application ready")
