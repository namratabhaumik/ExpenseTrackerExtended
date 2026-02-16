#!/usr/bin/env python
"""
Script to create DynamoDB table for expense tracker.
Run this once to set up your DynamoDB table.
"""

from dotenv import load_dotenv
import boto3
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import Django settings
sys.path.append(str(Path(__file__).parent.parent.parent))


# Load environment variables
load_dotenv()


def create_dynamodb_table():
    """Create DynamoDB table for expenses."""

    # Initialize DynamoDB client
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.environ.get('DYNAMODB_ENDPOINT_URL')
    )

    table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'expense-tracker-table')

    try:
        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'expense_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'expense_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f" DynamoDB table '{table_name}' created successfully!")

    except Exception as e:
        if 'Table already exists' in str(e):
            print(f"ℹ  Table '{table_name}' already exists.")
        else:
            print(f" Error creating table: {e}")


if __name__ == '__main__':
    create_dynamodb_table()
