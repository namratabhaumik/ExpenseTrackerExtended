#!/bin/bash
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application using the PORT environment variable provided by Cloud Run.
# Default to 8000 if PORT is not set.
echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec uvicorn expense_tracker.asgi:application --host 0.0.0.0 --port ${PORT:-8000}
