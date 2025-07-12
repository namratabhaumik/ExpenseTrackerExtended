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

# Try uvicorn instead of gunicorn
CMD ["uvicorn", "expense_tracker.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
