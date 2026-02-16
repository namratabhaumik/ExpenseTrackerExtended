"""AWS DynamoDB expense repository implementation."""

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import boto3
from django.conf import settings

from auth_app.services.expense_service import ExpenseRepository

logger = logging.getLogger(__name__)

# Lazy-load DynamoDB resource
_dynamodb_resource = None
_dynamodb_table = None


def get_dynamodb_table():
    """Get DynamoDB table (only used in production mode)."""
    global _dynamodb_resource, _dynamodb_table
    if _dynamodb_table is None:
        _dynamodb_resource = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
        )
        _dynamodb_table = _dynamodb_resource.Table(settings.DYNAMODB_TABLE_NAME)
    return _dynamodb_table


class DynamoDBExpenseRepository(ExpenseRepository):
    """Expense storage using AWS DynamoDB."""

    def __init__(self):
        self.table = get_dynamodb_table()

    def create(
        self, user_id: str, amount: float, category: str, description: str = ''
    ) -> Dict:
        """Create a new expense in DynamoDB."""
        try:
            expense_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            item = {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': Decimal(str(amount)),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': None,
            }

            self.table.put_item(Item=item)
            logger.info(f'Expense created: {expense_id} for user: {user_id}')

            return {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': float(item['amount']),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': None,
            }

        except Exception as e:
            logger.error(f'Error creating expense: {str(e)}', exc_info=True)
            raise

    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get all expenses for a user from DynamoDB."""
        try:
            response = self.table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
            )

            expenses = []
            for item in response.get('Items', []):
                # Convert Decimal to float for JSON serialization
                item['amount'] = float(item['amount'])
                expenses.append(item)

            logger.info(f'Retrieved {len(expenses)} expenses for user: {user_id}')
            return expenses

        except Exception as e:
            logger.error(f'Error retrieving expenses for user {user_id}: {str(e)}', exc_info=True)
            raise

    def get_by_id(self, expense_id: str) -> Optional[Dict]:
        """Get a specific expense by ID from DynamoDB."""
        try:
            response = self.table.get_item(Key={'expense_id': expense_id})

            item = response.get('Item')
            if item:
                item['amount'] = float(item['amount'])
                logger.info(f'Retrieved expense: {expense_id}')
                return item

            logger.warning(f'Expense not found: {expense_id}')
            return None

        except Exception as e:
            logger.error(f'Error retrieving expense {expense_id}: {str(e)}', exc_info=True)
            raise

    def update_receipt_url(self, expense_id: str, receipt_url: str) -> bool:
        """Update an expense with a receipt URL."""
        try:
            self.table.update_item(
                Key={'expense_id': expense_id},
                UpdateExpression='SET receipt_url = :receipt_url',
                ExpressionAttributeValues={':receipt_url': receipt_url},
            )
            logger.info(f'Receipt URL updated for expense: {expense_id}')
            return True

        except Exception as e:
            logger.error(f'Error updating receipt URL for {expense_id}: {str(e)}', exc_info=True)
            return False

    def add_expense_with_receipt(
        self,
        user_id: str,
        amount: float,
        category: str,
        description: str = '',
        receipt_url: Optional[str] = None,
    ) -> Dict:
        """Create a new expense with optional receipt URL."""
        try:
            expense_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            item = {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': Decimal(str(amount)),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': receipt_url,
            }

            self.table.put_item(Item=item)
            logger.info(f'Expense with receipt created: {expense_id} for user: {user_id}')

            return {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': float(item['amount']),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': receipt_url,
            }

        except Exception as e:
            logger.error(
                f'Error creating expense with receipt for user {user_id}: {str(e)}',
                exc_info=True,
            )
            raise
