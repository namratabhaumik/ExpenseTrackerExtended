import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from django.conf import settings

class DynamoDBExpenseService:
    """Service layer for DynamoDB expense operations."""
    def __init__(self):
        self.table = self.get_dynamodb_table()

    @staticmethod
    def get_dynamodb_table():
        dynamodb_resource = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL
        )
        return dynamodb_resource.Table(settings.DYNAMODB_TABLE_NAME)

    def create(self, user_id, amount, category, description=''):
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
        response = self.table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        expenses = []
        for item in response.get('Items', []):
            item['amount'] = float(item['amount'])
            expenses.append(item)
        return expenses

    def get_by_id(self, expense_id):
        response = self.table.get_item(Key={'expense_id': expense_id})
        item = response.get('Item')
        if item:
            item['amount'] = float(item['amount'])
        return item

    def update_receipt_url(self, expense_id, receipt_url):
        try:
            self.table.update_item(
                Key={'expense_id': expense_id},
                UpdateExpression='SET receipt_url = :receipt_url',
                ExpressionAttributeValues={':receipt_url': receipt_url}
            )
            return True
        except Exception as e:
            print(f"Error updating receipt URL: {str(e)}")
            return False

    def add_expense_with_receipt(self, user_id, amount, category, description='', receipt_url=None):
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
