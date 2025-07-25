# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Switch to project root
WORKDIR /app/expense_tracker

# Create log directory to prevent errors during build
RUN mkdir -p /app/logs

# Create the cache table for database-backed caching
# A dummy secret key is provided here just for the build process
RUN DJANGO_SECRET_KEY=dummy-for-build-only python manage.py createcachetable

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/expense_tracker/
RUN chmod +x /app/expense_tracker/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/expense_tracker/entrypoint.sh"]

# Default command (can be overridden)
CMD ["uvicorn", "expense_tracker.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
