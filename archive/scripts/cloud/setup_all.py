#!/usr/bin/env python
"""
Master setup script for cloud resources.
This script sets up required AWS resources for cloud deployment.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


def main():
    """Run all cloud setup scripts in the correct order."""
    print(" Setting up Expense Tracker Cloud Resources...")
    print("=" * 50)

    # Setup DynamoDB
    print("\n Setting up DynamoDB...")
    try:
        from cloud.setup_dynamodb import create_dynamodb_table
        create_dynamodb_table()
    except Exception as e:
        print(f" DynamoDB setup failed: {e}")
        return False

    # S3 bucket already exists - just verify
    print("\n  Checking S3 bucket...")
    try:
        from cloud.check_s3 import check_s3_buckets
        check_s3_buckets()
    except Exception as e:
        print(f"  S3 check failed: {e}")
        print("   (This is okay if you're using an existing bucket)")

    print("\n" + "=" * 50)
    print(" Setup completed!")
    print("\nNext steps:")
    print("1. Deploy to Cloud Run: gcloud run deploy ...")
    print("2. Set environment variables in Cloud Run settings")
    print("3. Check logs in Cloud Run console")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
