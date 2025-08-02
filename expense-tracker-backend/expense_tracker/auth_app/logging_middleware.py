"""
Middleware for automatic request/response logging with structured data.
This middleware integrates with Google Cloud Operations Suite for
comprehensive monitoring and debugging capabilities.
"""

import time
import logging
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from utils.logging_config import log_request_start, log_request_end, log_error, get_structured_logger


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that automatically logs all requests and responses with
    structured data for Google Cloud Operations Suite integration.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = get_structured_logger('request')

    def process_request(self, request: HttpRequest) -> None:
        """Log the start of a request."""
        # Start timing the request
        request.start_time = time.time()

        # Extract user ID if available
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)

        # Log request start
        request.request_id = log_request_start(request, user_id)

        # Add request ID to request object for use in views
        request.request_id = request.request_id

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log the completion of a request with performance metrics."""
        if hasattr(request, 'start_time') and hasattr(request, 'request_id'):
            # Calculate request duration
            duration_ms = (time.time() - request.start_time) * 1000

            # Extract user ID if available
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)

            # Log request completion
            log_request_end(
                request.request_id,
                response.status_code,
                duration_ms,
                user_id
            )

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Log exceptions with structured data for debugging."""
        # Extract user ID if available
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)

        # Create context for the error
        context = {
            'request_id': getattr(request, 'request_id', None),
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
        }

        # Log the error
        log_error(exception, context, user_id)


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs performance metrics for slow requests.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = get_structured_logger('performance')
        # Log requests that take longer than 1 second
        self.slow_request_threshold = 1000  # milliseconds

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log slow requests for performance monitoring."""
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000

            if duration_ms > self.slow_request_threshold:
                # Extract user ID if available
                user_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = str(request.user.id)

                self.logger.warning(
                    "Slow request detected",
                    extra={
                        'request_id': getattr(request, 'request_id', None),
                        'user_id': user_id,
                        'method': request.method,
                        'path': request.path,
                        'duration_ms': duration_ms,
                        'threshold_ms': self.slow_request_threshold,
                        'status_code': response.status_code,
                    }
                )

        return response
