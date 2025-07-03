from django.db import models
import boto3
import json
import uuid
from datetime import datetime
from decimal import Decimal
from django.conf import settings

# Create your models here.


class DynamoDBExpense:
    """DynamoDB model for expenses."""

    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL
        )
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME)

    def create(self, user_id, amount, category, description=''):
        """Create a new expense."""
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
        response = self.table.get_item(
            Key={'expense_id': expense_id}
        )

        item = response.get('Item')
        if item:
            item['amount'] = float(item['amount'])

        return item

    def update_receipt_url(self, expense_id, receipt_url):
        """Update an expense with a receipt URL."""
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
