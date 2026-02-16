#!/bin/bash
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application using the PORT environment variable provided by Cloud Run.
# Default to 8000 if PORT is not set.
echo "Starting Gunicorn server on port ${PORT:-8000}..."
exec gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class sync --timeout 120
