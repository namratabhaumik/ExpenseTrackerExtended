import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from auth_app.services.DynamoDBExpenseService import DynamoDBExpenseService

class DynamoDBExpenseServiceTest(unittest.TestCase):
    @patch('auth_app.services.DynamoDBExpenseService.DynamoDBExpenseService.get_dynamodb_table')
    def setUp(self, mock_get_table):
        self.mock_table = MagicMock()
        mock_get_table.return_value = self.mock_table
        self.service = DynamoDBExpenseService()

    def test_create_expense(self):
        user_id = 'user-1'
        amount = 10.5
        category = 'Food'
        description = 'Lunch'
        result = self.service.create(user_id, amount, category, description)
        self.mock_table.put_item.assert_called_once()
        self.assertEqual(result['user_id'], user_id)
        self.assertEqual(result['amount'], Decimal(str(amount)))
        self.assertEqual(result['category'], category)
        self.assertEqual(result['description'], description)
        self.assertIsNone(result['receipt_url'])

    def test_get_by_user(self):
        user_id = 'user-1'
        self.mock_table.scan.return_value = {
            'Items': [
                {'expense_id': 'e1', 'user_id': user_id, 'amount': Decimal('10.5'), 'category': 'Food', 'description': 'Lunch', 'timestamp': '2024-01-01T00:00:00', 'receipt_url': None}
            ]
        }
        expenses = self.service.get_by_user(user_id)
        self.mock_table.scan.assert_called_once()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0]['user_id'], user_id)
        self.assertIsInstance(expenses[0]['amount'], float)

    def test_get_by_id(self):
        expense_id = 'e1'
        self.mock_table.get_item.return_value = {
            'Item': {'expense_id': expense_id, 'user_id': 'user-1', 'amount': Decimal('10.5'), 'category': 'Food', 'description': 'Lunch', 'timestamp': '2024-01-01T00:00:00', 'receipt_url': None}
        }
        item = self.service.get_by_id(expense_id)
        self.mock_table.get_item.assert_called_once_with(Key={'expense_id': expense_id})
        self.assertEqual(item['expense_id'], expense_id)
        self.assertIsInstance(item['amount'], float)

    def test_update_receipt_url_success(self):
        expense_id = 'e1'
        self.mock_table.update_item.return_value = {}
        result = self.service.update_receipt_url(expense_id, 'http://example.com/receipt.jpg')
        self.mock_table.update_item.assert_called_once()
        self.assertTrue(result)

    def test_update_receipt_url_failure(self):
        expense_id = 'e1'
        self.mock_table.update_item.side_effect = Exception('fail')
        result = self.service.update_receipt_url(expense_id, 'bad')
        self.assertFalse(result)

    def test_add_expense_with_receipt(self):
        user_id = 'user-1'
        amount = 20
        category = 'Travel'
        description = 'Taxi'
        receipt_url = 'http://example.com/receipt.jpg'
        result = self.service.add_expense_with_receipt(user_id, amount, category, description, receipt_url)
        self.mock_table.put_item.assert_called_once()
        self.assertEqual(result['user_id'], user_id)
        self.assertEqual(result['receipt_url'], receipt_url)

if __name__ == '__main__':
    unittest.main()
