#!/usr/bin/env python
"""
Script to check S3 buckets and verify configuration.
"""

from dotenv import load_dotenv
import boto3
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


# Load environment variables
load_dotenv()


def check_s3_buckets():
    """Check all S3 buckets and verify configuration."""

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    bucket_name = os.environ.get('S3_BUCKET_NAME', 'expense-tracker-receipts')

    print(" Checking S3 Configuration...")
    print("=" * 50)
    print(f"Expected bucket name: {bucket_name}")
    print(f"AWS Region: {os.environ.get('AWS_REGION', 'us-east-1')}")
    print(
        f"AWS Access Key ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')[:10]}...")
    print()

    try:
        # List all buckets
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]

        print(" All S3 Buckets in your account:")
        for bucket in buckets:
            if bucket == bucket_name:
                print(f"   {bucket} (MATCHES EXPECTED NAME)")
            else:
                print(f"   {bucket}")

        print()

        # Check if expected bucket exists
        if bucket_name in buckets:
            print(f" Bucket '{bucket_name}' exists!")

            # Test bucket access
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(" Bucket is accessible")

                # List some objects (if any)
                try:
                    objects = s3_client.list_objects_v2(
                        Bucket=bucket_name, MaxKeys=5)
                    if 'Contents' in objects:
                        print(
                            f" Found {len(objects['Contents'])} objects in bucket")
                    else:
                        print(" Bucket is empty")
                except Exception as e:
                    print(f"  Could not list objects: {e}")

            except Exception as e:
                print(f" Bucket exists but not accessible: {e}")
        else:
            print(f" Bucket '{bucket_name}' does not exist!")
            print("Available buckets:")
            for bucket in buckets:
                print(f"  - {bucket}")

            # Check for similar names
            similar_buckets = [
                b for b in buckets if 'receipt' in b.lower() or 'expense' in b.lower()]
            if similar_buckets:
                print(f"\n Similar buckets found: {similar_buckets}")

    except Exception as e:
        print(f" Error checking S3: {e}")


if __name__ == '__main__':
    check_s3_buckets()
