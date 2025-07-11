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

# Run using Gunicorn with optimized settings for Cloud Run
CMD ["gunicorn", "expense_tracker.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=1", "--timeout=90"]
