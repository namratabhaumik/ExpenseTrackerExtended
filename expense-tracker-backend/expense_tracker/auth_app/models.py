from django.db import models
import boto3
import json
import uuid
from datetime import datetime
from decimal import Decimal
from django.conf import settings
import os

# Create your models here.

# Check if in local demo mode
IS_LOCAL_DEMO = os.environ.get('LOCAL_DEMO', 'false').lower() == 'true'

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
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL
        )
        _dynamodb_table = _dynamodb_resource.Table(
            settings.DYNAMODB_TABLE_NAME)
    return _dynamodb_table


class DynamoDBExpense:
    """
    Expense storage abstraction.
    Uses DynamoDB in production, SQLite (Django ORM) in local demo mode.
    """

    def __init__(self):
        self.is_local = IS_LOCAL_DEMO
        if not self.is_local:
            self.table = get_dynamodb_table()

    def create(self, user_id, amount, category, description=''):
        """Create a new expense."""
        if self.is_local:
            # Use Django model for local development
            expense = Expense.objects.create(
                user_id=user_id,
                amount=amount,
                category=category,
                description=description
            )
            return {
                'expense_id': str(expense.id),
                'user_id': expense.user_id,
                'amount': float(expense.amount),
                'category': expense.category,
                'description': expense.description,
                'timestamp': expense.timestamp.isoformat(),
                'receipt_url': expense.receipt_url
            }
        else:
            # Use DynamoDB for production
            expense_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            item = {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': Decimal(str(amount)),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': None
            }

            self.table.put_item(Item=item)
            return item

    def get_by_user(self, user_id):
        """Get all expenses for a user."""
        if self.is_local:
            # Use Django ORM
            expenses = Expense.objects.filter(user_id=user_id).order_by('-timestamp')
            return [
                {
                    'expense_id': str(exp.id),
                    'user_id': exp.user_id,
                    'amount': float(exp.amount),
                    'category': exp.category,
                    'description': exp.description,
                    'timestamp': exp.timestamp.isoformat(),
                    'receipt_url': exp.receipt_url
                }
                for exp in expenses
            ]
        else:
            # Use DynamoDB
            response = self.table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={
                    ':user_id': user_id
                }
            )

            expenses = []
            for item in response.get('Items', []):
                # Convert Decimal to float for JSON serialization
                item['amount'] = float(item['amount'])
                expenses.append(item)

            return expenses

    def get_by_id(self, expense_id):
        """Get expense by ID."""
        if self.is_local:
            # Use Django ORM
            try:
                expense = Expense.objects.get(id=expense_id)
                return {
                    'expense_id': str(expense.id),
                    'user_id': expense.user_id,
                    'amount': float(expense.amount),
                    'category': expense.category,
                    'description': expense.description,
                    'timestamp': expense.timestamp.isoformat(),
                    'receipt_url': expense.receipt_url
                }
            except Expense.DoesNotExist:
                return None
        else:
            # Use DynamoDB
            response = self.table.get_item(
                Key={'expense_id': expense_id}
            )

            item = response.get('Item')
            if item:
                item['amount'] = float(item['amount'])

            return item

    def update_receipt_url(self, expense_id, receipt_url):
        """Update an expense with a receipt URL."""
        if self.is_local:
            # Use Django ORM
            try:
                expense = Expense.objects.get(id=expense_id)
                expense.receipt_url = receipt_url
                expense.save()
                return True
            except Expense.DoesNotExist:
                return False
        else:
            # Use DynamoDB
            try:
                self.table.update_item(
                    Key={'expense_id': expense_id},
                    UpdateExpression='SET receipt_url = :receipt_url',
                    ExpressionAttributeValues={
                        ':receipt_url': receipt_url
                    }
                )
                return True
            except Exception as e:
                print(f"Error updating receipt URL: {str(e)}")
                return False

    def add_expense_with_receipt(self, user_id, amount, category, description='', receipt_url=None):
        """Create a new expense with optional receipt URL."""
        if self.is_local:
            # Use Django model
            expense = Expense.objects.create(
                user_id=user_id,
                amount=amount,
                category=category,
                description=description,
                receipt_url=receipt_url
            )
            return {
                'expense_id': str(expense.id),
                'user_id': expense.user_id,
                'amount': float(expense.amount),
                'category': expense.category,
                'description': expense.description,
                'timestamp': expense.timestamp.isoformat(),
                'receipt_url': expense.receipt_url
            }
        else:
            # Use DynamoDB
            expense_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            item = {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': Decimal(str(amount)),
                'category': category,
                'description': description,
                'timestamp': timestamp,
                'receipt_url': receipt_url
            }

            self.table.put_item(Item=item)
            return item

# Keep the Django model for compatibility but mark it as deprecated


class Expense(models.Model):
    """Legacy Django model - deprecated in favor of DynamoDB."""
    user_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_id} - {self.amount} - {self.category}"
