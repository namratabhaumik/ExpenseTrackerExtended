#!/usr/bin/env python
"""
Master setup script for expense tracker backend.
This script sets up required AWS resources.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


def main():
    """Run all setup scripts in the correct order."""
    print("🚀 Setting up Expense Tracker Backend...")
    print("=" * 50)

    # Setup DynamoDB
    print("\n📊 Setting up DynamoDB...")
    try:
        from setup_dynamodb import create_dynamodb_table
        create_dynamodb_table()
    except Exception as e:
        print(f"❌ DynamoDB setup failed: {e}")
        return False

    # S3 bucket already exists - just verify
    print("\n☁️  Checking S3 bucket...")
    try:
        from check_s3 import check_s3_buckets
        check_s3_buckets()
    except Exception as e:
        print(f"⚠️  S3 check failed: {e}")
        print("   (This is okay if you're using an existing bucket)")

    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\nNext steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Test endpoints with curl commands")
    print("3. Check logs/django.log for any issues")
    print("\nNote: Using existing S3 bucket 'my-finance-tracker-receipts'")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
