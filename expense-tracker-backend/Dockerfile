# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Set the default directory where the commands will run
WORKDIR /app/expense_tracker

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
