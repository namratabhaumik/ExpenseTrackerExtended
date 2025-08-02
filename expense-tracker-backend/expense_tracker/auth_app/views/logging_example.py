"""
Example of how to use structured logging in Django views.
This file demonstrates best practices for logging in the Expense Tracker application.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from utils.logging_config import get_structured_logger, log_error


# Get a structured logger for this module
logger = get_structured_logger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def example_view(request):
    """
    Example view demonstrating structured logging best practices.
    """
    try:
        # Log the start of processing
        logger.info(
            "Processing example request",
            extra={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'parameters': dict(request.GET.items()),
            }
        )

        # Simulate some processing
        result = perform_expensive_operation()

        # Log successful completion
        logger.info(
            "Example request completed successfully",
            extra={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'result_count': len(result),
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Example operation completed',
            'data': result
        })

    except Exception as e:
        # Log the error with context
        log_error(
            e,
            context={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'method': request.method,
                'path': request.path,
                'parameters': dict(request.GET.items()),
            },
            user_id=getattr(request, 'user_id', None)
        )

        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing the request'
        }, status=500)


def perform_expensive_operation():
    """
    Example function that performs some expensive operation.
    Demonstrates logging at different levels.
    """
    logger.debug("Starting expensive operation")

    # Simulate some work
    import time
    time.sleep(0.1)

    # Log progress
    logger.info("Expensive operation in progress",
                extra={'step': 'processing'})

    # Simulate potential issues
    import random
    if random.random() < 0.1:  # 10% chance of warning
        logger.warning(
            "Performance degradation detected",
            extra={
                'operation': 'expensive_operation',
                'duration_ms': 100,
                'threshold_ms': 50,
            }
        )

    result = [f"item_{i}" for i in range(10)]

    logger.debug("Expensive operation completed",
                 extra={'result_count': len(result)})
    return result


@csrf_exempt
@require_http_methods(["POST"])
def example_create_view(request):
    """
    Example view for creating resources with validation logging.
    """
    try:
        # Log incoming data (be careful not to log sensitive information)
        logger.info(
            "Processing create request",
            extra={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'content_type': request.content_type,
                'content_length': len(request.body) if request.body else 0,
            }
        )

        # Validate input
        if not request.body:
            logger.warning(
                "Empty request body received",
                extra={
                    'user_id': getattr(request, 'user_id', None),
                    'request_id': getattr(request, 'request_id', None),
                }
            )
            return JsonResponse({
                'status': 'error',
                'message': 'Request body is required'
            }, status=400)

        # Process the request
        data = request.POST if request.POST else {}

        # Log validation results
        logger.info(
            "Request validation completed",
            extra={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'field_count': len(data),
                'has_required_fields': all(key in data for key in ['name', 'value']),
            }
        )

        # Simulate creation
        import time
        created_id = f"item_{int(time.time())}"

        logger.info(
            "Resource created successfully",
            extra={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'created_id': created_id,
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Resource created successfully',
            'id': created_id
        })

    except Exception as e:
        log_error(
            e,
            context={
                'user_id': getattr(request, 'user_id', None),
                'request_id': getattr(request, 'request_id', None),
                'method': request.method,
                'path': request.path,
                'operation': 'create',
            },
            user_id=getattr(request, 'user_id', None)
        )

        return JsonResponse({
            'status': 'error',
            'message': 'Failed to create resource'
        }, status=500)


# Example of logging in a background task or service
def background_task_example():
    """
    Example of logging in background tasks or services.
    """
    task_logger = get_structured_logger('background_task')

    task_logger.info("Starting background task")

    try:
        # Simulate some background work
        import time
        time.sleep(1)

        task_logger.info(
            "Background task completed",
            extra={
                'task_type': 'data_processing',
                'records_processed': 1000,
                'duration_seconds': 1,
            }
        )

    except Exception as e:
        task_logger.error(
            "Background task failed",
            extra={
                'task_type': 'data_processing',
                'error_type': type(e).__name__,
                'error_message': str(e),
            },
            exc_info=True
        )
        raise


# Example of logging database operations
def database_operation_example():
    """
    Example of logging database operations.
    """
    db_logger = get_structured_logger('database')

    db_logger.info("Starting database operation")

    try:
        # Simulate database query
        import time
        start_time = time.time()
        time.sleep(0.05)  # Simulate query time
        duration_ms = (time.time() - start_time) * 1000

        db_logger.info(
            "Database query completed",
            extra={
                'operation': 'SELECT',
                'table': 'expenses',
                'duration_ms': duration_ms,
                'rows_returned': 50,
            }
        )

        # Log slow queries
        if duration_ms > 100:
            db_logger.warning(
                "Slow database query detected",
                extra={
                    'operation': 'SELECT',
                    'table': 'expenses',
                    'duration_ms': duration_ms,
                    'threshold_ms': 100,
                }
            )

    except Exception as e:
        db_logger.error(
            "Database operation failed",
            extra={
                'operation': 'SELECT',
                'table': 'expenses',
                'error_type': type(e).__name__,
                'error_message': str(e),
            },
            exc_info=True
        )
        raise
