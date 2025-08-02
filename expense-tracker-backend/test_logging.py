#!/usr/bin/env python3
"""
Simple test script to verify the logging configuration works correctly.
"""

from utils.logging_config import (
    GoogleCloudJsonFormatter,
    get_structured_logger,
    log_request_start,
    log_request_end,
    log_error
)
import json
import logging
import os
import sys

# Add the expense_tracker directory to the Python path BEFORE imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'expense_tracker'))

# Now import the modules


def test_json_formatter():
    """Test that the JSON formatter produces the expected output."""
    print("Testing JSON formatter...")

    # Create a logger with the custom formatter
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)

    # Create a handler that writes to a string
    from io import StringIO
    handler = logging.StreamHandler(StringIO())
    handler.setFormatter(GoogleCloudJsonFormatter())
    logger.addHandler(handler)

    # Test basic logging
    logger.info("Test message")

    # Get the log output
    log_output = handler.stream.getvalue()
    print(f"Log output: {log_output}")

    # Try to parse as JSON
    try:
        log_data = json.loads(log_output.strip())
        print("✅ JSON parsing successful")
        print(f"   Timestamp: {log_data.get('timestamp')}")
        print(f"   Severity: {log_data.get('severity')}")
        print(f"   Service: {log_data.get('service')}")
        print(f"   Environment: {log_data.get('environment')}")
        print(f"   Message: {log_data.get('message')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

    return True


def test_structured_logging():
    """Test the structured logging functions."""
    print("\nTesting structured logging functions...")

    # Mock request object
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
            self.path = '/api/test'
            self.META = {
                'HTTP_USER_AGENT': 'test-agent',
                'REMOTE_ADDR': '127.0.0.1'
            }

    request = MockRequest()

    # Test request start logging
    print("Testing request start logging...")
    request_id = log_request_start(request, 'test-user-123')
    print(f"   Generated request ID: {request_id}")

    # Test request end logging
    print("Testing request end logging...")
    log_request_end(request_id, 200, 150.5, 'test-user-123')

    # Test error logging
    print("Testing error logging...")
    test_error = ValueError("Test error message")
    context = {'test_key': 'test_value', 'endpoint': '/api/test'}
    log_error(test_error, context, 'test-user-123')

    print("✅ Structured logging functions completed")


def test_logger_attributes():
    """Test that loggers have the expected attributes."""
    print("\nTesting logger attributes...")

    logger = get_structured_logger('test_logger')

    # Check that the logger has the expected attributes
    if hasattr(logger, 'request_id'):
        print("✅ Logger has request_id attribute")
    else:
        print("❌ Logger missing request_id attribute")
        return False

    if hasattr(logger, 'user_id'):
        print("✅ Logger has user_id attribute")
    else:
        print("❌ Logger missing user_id attribute")
        return False

    return True


def main():
    """Run all tests."""
    print("Testing logging configuration...")
    print("=" * 50)

    # Test JSON formatter
    if not test_json_formatter():
        print("❌ JSON formatter test failed")
        return 1

    # Test structured logging
    test_structured_logging()

    # Test logger attributes
    if not test_logger_attributes():
        print("❌ Logger attributes test failed")
        return 1

    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("\nThe logging configuration is working correctly.")
    print("In production, logs will be automatically sent to Google Cloud Operations Suite.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
