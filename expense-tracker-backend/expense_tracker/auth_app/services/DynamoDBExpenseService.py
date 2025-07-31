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
        # Ensure expense_id is a string (it might be a UUID object)
        expense_id_str = str(expense_id)
        response = self.table.get_item(Key={'expense_id': expense_id_str})
        item = response.get('Item')
        if item:
            item['amount'] = float(item['amount'])
        return item

    def update_receipt_url(self, expense_id, receipt_url):
        try:
            # Ensure expense_id is a string (it might be a UUID object)
            expense_id_str = str(expense_id)
            self.table.update_item(
                Key={'expense_id': expense_id_str},
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
        
    def update_expense(self, expense_id, user_id, amount=None, category=None, description=None, receipt_url=None):
        """Update an existing expense."""
        try:
            # Ensure expense_id is a string (it might be a UUID object)
            expense_id_str = str(expense_id)
            
            # First, verify the expense exists and belongs to the user
            expense = self.get_by_id(expense_id_str)
            if not expense or expense['user_id'] != user_id:
                return None
                
            # Build update expression and attribute values
            update_expression = []
            expression_attribute_values = {}
            
            if amount is not None:
                update_expression.append('amount = :amount')
                expression_attribute_values[':amount'] = Decimal(str(amount))
                
            if category is not None:
                update_expression.append('#category = :category')
                expression_attribute_values[':category'] = category
                
            if description is not None:
                update_expression.append('description = :description')
                expression_attribute_values[':description'] = description
                
            if receipt_url is not None:
                update_expression.append('receipt_url = :receipt_url')
                expression_attribute_values[':receipt_url'] = receipt_url
                
            # Add timestamp for last update
            update_expression.append('last_updated = :last_updated')
            expression_attribute_values[':last_updated'] = datetime.utcnow().isoformat()
            
            if not update_expression:
                return expense  # No updates to make
                
            # Perform the update
            response = self.table.update_item(
                Key={'expense_id': expense_id_str},
                UpdateExpression='SET ' + ', '.join(update_expression),
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames={
                    '#category': 'category'  # category is a reserved word in DynamoDB
                },
                ReturnValues='ALL_NEW'
            )
            
            updated_item = response.get('Attributes', {})
            if updated_item and 'amount' in updated_item:
                updated_item['amount'] = float(updated_item['amount'])
                
            return updated_item
            
        except Exception as e:
            print(f"Error updating expense: {str(e)}")
            return None
            
    def delete_expense(self, expense_id, user_id):
        """Delete an expense if it belongs to the specified user."""
        try:
            # Ensure expense_id is a string (it might be a UUID object)
            expense_id_str = str(expense_id)
            
            # First verify the expense exists and belongs to the user
            expense = self.get_by_id(expense_id_str)
            if not expense or expense['user_id'] != user_id:
                return False
                
            # Delete the expense
            self.table.delete_item(
                Key={'expense_id': expense_id_str}
            )
            return True
            
        except Exception as e:
            print(f"Error deleting expense: {str(e)}")
            return False
