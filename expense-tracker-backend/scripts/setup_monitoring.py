#!/usr/bin/env python3
"""
Setup script for Google Cloud Operations Suite monitoring.
This script helps deploy the monitoring dashboard and alerts for the Expense Tracker application.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    return result


def get_project_id() -> str:
    """Get the current Google Cloud project ID."""
    result = run_command("gcloud config get-value project")
    project_id = result.stdout.strip()

    if not project_id:
        print("Error: No Google Cloud project configured.")
        print("Please run: gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)

    return project_id


def create_dashboard(project_id: str) -> None:
    """Create the monitoring dashboard in Google Cloud Operations Suite."""
    dashboard_file = Path(__file__).parent.parent / \
        "monitoring" / "dashboard.json"

    if not dashboard_file.exists():
        print(f"Error: Dashboard file not found at {dashboard_file}")
        return

    print(f"Creating dashboard in project: {project_id}")

    # Create the dashboard using gcloud
    command = f"gcloud monitoring dashboards create --project={project_id} --config-from-file={dashboard_file}"
    result = run_command(command, check=False)

    if result.returncode == 0:
        print("Dashboard created successfully!")
    else:
        print("Failed to create dashboard. You may need to create it manually in the Google Cloud Console.")
        print("Dashboard configuration is available at:", dashboard_file)


def create_alert_policy(project_id: str) -> None:
    """Create the alerting policy in Google Cloud Operations Suite."""
    alerts_file = Path(__file__).parent.parent / "monitoring" / "alerts.json"

    if not alerts_file.exists():
        print(f"Error: Alerts file not found at {alerts_file}")
        return

    print(f"Creating alert policy in project: {project_id}")

    # Note: Alert policies require more complex setup and are better created manually
    # through the Google Cloud Console or using the Cloud Monitoring API
    print("Alert policy creation requires manual setup.")
    print("Please create the alert policy manually using the configuration at:", alerts_file)
    print("Or use the Google Cloud Console: https://console.cloud.google.com/monitoring/alerting")


def setup_logging() -> None:
    """Set up logging configuration for the application."""
    print("Setting up structured logging...")

    # Check if required environment variables are set
    required_vars = ['GOOGLE_APPLICATION_CREDENTIALS']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print(
            "\nFor production deployment on Cloud Run, these are automatically configured.")
        print("For local development, you may need to set up authentication.")

    print("Logging setup complete!")


def main() -> None:
    """Main setup function."""
    print("Setting up Google Cloud Operations Suite monitoring for Expense Tracker")
    print("=" * 70)

    # Check if gcloud is installed and authenticated
    try:
        run_command("gcloud --version")
    except FileNotFoundError:
        print("Error: gcloud CLI is not installed or not in PATH")
        print(
            "Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

    # Check authentication
    result = run_command(
        "gcloud auth list --filter=status:ACTIVE --format='value(account)'", check=False)
    if result.returncode != 0 or not result.stdout.strip():
        print("Error: Not authenticated with Google Cloud")
        print("Please run: gcloud auth login")
        sys.exit(1)

    # Get project ID
    project_id = get_project_id()
    print(f"Using project: {project_id}")

    # Setup components
    setup_logging()
    create_dashboard(project_id)
    create_alert_policy(project_id)

    print("\n" + "=" * 70)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Deploy your application to Cloud Run")
    print("2. View logs in Google Cloud Operations Suite: https://console.cloud.google.com/logs")
    print("3. View metrics in the dashboard: https://console.cloud.google.com/monitoring/dashboards")
    print("4. Configure alert notifications in the Google Cloud Console")


if __name__ == "__main__":
    main()
