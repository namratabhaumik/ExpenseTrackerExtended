"""
Logging configuration for Google Cloud Operations Suite integration.
This module provides structured JSON logging that works seamlessly with
Google Cloud's logging and monitoring services.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

import google.cloud.logging
from pythonjsonlogger import jsonlogger


class GoogleCloudJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that outputs logs in a format optimized for
    Google Cloud Operations Suite.
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record for Google Cloud compatibility."""
        super().add_fields(log_record, record, message_dict)

        # Ensure timestamp is in ISO format for Google Cloud
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        # Add severity level that Google Cloud expects
        log_record['severity'] = record.levelname

        # Add service context for better log organization
        log_record['service'] = 'expense-tracker-backend'

        # Add environment information
        log_record['environment'] = 'production' if os.environ.get(
            'CLOUD_RUN', 'false').lower() == 'true' else 'development'

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id


def setup_google_cloud_logging() -> None:
    """
    Set up Google Cloud Logging client for production environment.
    This should be called early in the application startup.
    """
    if os.environ.get('CLOUD_RUN', 'false').lower() == 'true':
        try:
            # Initialize Google Cloud Logging client
            client = google.cloud.logging.Client()
            client.setup_logging()

            # Log successful setup
            logging.info("Google Cloud Logging initialized successfully")
        except Exception as e:
            # Fallback to console logging if Google Cloud setup fails
            logging.warning(
                f"Failed to initialize Google Cloud Logging: {e}. Falling back to console logging.")


def get_structured_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for structured logging.

    Args:
        name: The name of the logger

    Returns:
        A logger instance configured for structured logging
    """
    logger = logging.getLogger(name)

    # Add custom attributes for request tracking
    logger.request_id = None
    logger.user_id = None

    return logger


def log_request_start(request, user_id: str = None) -> str:
    """
    Log the start of a request with structured data.

    Args:
        request: Django request object
        user_id: Optional user ID for the request

    Returns:
        A unique request ID for tracking
    """
    import uuid

    request_id = str(uuid.uuid4())
    logger = get_structured_logger('request')
    logger.request_id = request_id
    logger.user_id = user_id

    logger.info(
        "Request started",
        extra={
            'request_id': request_id,
            'user_id': user_id,
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
        }
    )

    return request_id


def log_request_end(request_id: str, status_code: int, duration_ms: float, user_id: str = None) -> None:
    """
    Log the end of a request with performance metrics.

    Args:
        request_id: The request ID from log_request_start
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID for the request
    """
    logger = get_structured_logger('request')
    logger.request_id = request_id
    logger.user_id = user_id

    logger.info(
        "Request completed",
        extra={
            'request_id': request_id,
            'user_id': user_id,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'success': 200 <= status_code < 400,
        }
    )


def log_error(error: Exception, context: Dict[str, Any] = None, user_id: str = None) -> None:
    """
    Log an error with structured data for better debugging.

    Args:
        error: The exception that occurred
        context: Additional context information
        user_id: Optional user ID for the error
    """
    logger = get_structured_logger('error')
    logger.user_id = user_id

    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'user_id': user_id,
    }

    if context:
        error_data.update(context)

    logger.error(
        f"Error occurred: {error}",
        extra=error_data,
        exc_info=True
    )
