"""
Django application initialization.
This module sets up Google Cloud logging when the application starts.
"""

import os

# Initialize Google Cloud logging for production
if os.environ.get('CLOUD_RUN', 'false').lower() == 'true':
    from utils.logging_config import setup_google_cloud_logging
    setup_google_cloud_logging()
