"""Unit tests for models.py (DynamoDBExpense and Expense model)."""

from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from auth_app.models import DynamoDBExpense, Expense


class ExpenseModelTest(TestCase):
    """Test Django Expense model."""

    def setUp(self):
        """Create a test user for expense tests."""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_expense_creation(self):
        """Test creating an expense"""
        expense = Expense.objects.create(
            user=self.user,
            amount=25.50,
            category='Food',
            description='Lunch'
        )

        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.amount, Decimal('25.50'))
        self.assertEqual(expense.category, 'Food')
        self.assertEqual(expense.description, 'Lunch')

    def test_expense_timestamp_auto_set(self):
        """Test expense timestamp is set automatically"""
        expense = Expense.objects.create(
            user=self.user,
            amount=10.00,
            category='Transport'
        )

        self.assertIsNotNone(expense.timestamp)

    def test_expense_string_representation(self):
        """Test expense string representation"""
        expense = Expense.objects.create(
            user=self.user,
            amount=15.00,
            category='Food'
        )

        result = str(expense)
        self.assertIn(self.user.email, result)
        self.assertIn('15', result)
        self.assertIn('Food', result)

    def test_expense_string_representation_no_user(self):
        """Test expense string representation without user"""
        expense = Expense.objects.create(
            user=None,
            amount=20.00,
            category='Other'
        )

        result = str(expense)
        self.assertIn('No User', result)
        self.assertIn('20', result)
        self.assertIn('Other', result)

    def test_expense_optional_fields(self):
        """Test expense with optional fields"""
        expense = Expense.objects.create(
            user=self.user,
            amount=50.00,
            category='Travel',
            description='Flight ticket',
            receipt_url='https://example.com/receipt.jpg'
        )

        self.assertEqual(expense.receipt_url, 'https://example.com/receipt.jpg')

    def test_expense_blank_fields(self):
        """Test expense with blank optional fields"""
        expense = Expense.objects.create(
            user=self.user,
            amount=30.00,
            category='Entertainment'
        )

        self.assertIsNone(expense.description)
        self.assertIsNone(expense.receipt_url)

    def test_expense_ordering(self):
        """Test expenses are ordered by timestamp (newest first)"""
        expense1 = Expense.objects.create(
            user=self.user, amount=10.00, category='Food'
        )
        expense2 = Expense.objects.create(
            user=self.user, amount=20.00, category='Transport'
        )

        expenses = list(Expense.objects.all())
        self.assertEqual(expenses[0].id, expense2.id)
        self.assertEqual(expenses[1].id, expense1.id)

    def test_expense_cascading_delete(self):
        """Test expenses are deleted when user is deleted"""
        expense = Expense.objects.create(
            user=self.user, amount=10.00, category='Food'
        )
        expense_id = expense.id

        self.user.delete()

        self.assertFalse(Expense.objects.filter(id=expense_id).exists())


@override_settings(IS_LOCAL_DEMO=True)
class DynamoDBExpenseLocalTest(TestCase):
    """Test DynamoDBExpense in local demo mode (using Django ORM)."""

    def setUp(self):
        """Set up test user and expense manager"""
        self.user = User.objects.create_user(
            username='localtest@example.com',
            email='localtest@example.com',
            password='testpass123'
        )
        self.expense_manager = DynamoDBExpense()

    def test_local_create_expense(self):
        """Test creating expense in local mode"""
        result = self.expense_manager.create(
            user_id=self.user.id,
            amount=25.50,
            category='Food',
            description='Lunch'
        )

        self.assertIn('expense_id', result)
        self.assertEqual(result['amount'], 25.50)
        self.assertEqual(result['category'], 'Food')
        self.assertEqual(result['description'], 'Lunch')

    def test_local_get_by_user(self):
        """Test retrieving expenses by user in local mode"""
        self.expense_manager.create(
            user_id=self.user.id,
            amount=10.00,
            category='Transport'
        )
        self.expense_manager.create(
            user_id=self.user.id,
            amount=20.00,
            category='Food'
        )

        expenses = self.expense_manager.get_by_user(self.user.id)

        self.assertEqual(len(expenses), 2)
        self.assertTrue(all(e['user_id'] == self.user.id for e in expenses))

    def test_local_get_by_id(self):
        """Test retrieving specific expense by ID in local mode"""
        created = self.expense_manager.create(
            user_id=self.user.id,
            amount=15.00,
            category='Entertainment'
        )
        expense_id = created['expense_id']

        result = self.expense_manager.get_by_id(expense_id)

        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 15.00)
        self.assertEqual(result['category'], 'Entertainment')

    def test_local_get_by_id_not_found(self):
        """Test retrieving non-existent expense returns None"""
        result = self.expense_manager.get_by_id(99999)

        self.assertIsNone(result)

    def test_local_update_receipt_url(self):
        """Test updating receipt URL in local mode"""
        created = self.expense_manager.create(
            user_id=self.user.id,
            amount=30.00,
            category='Travel'
        )
        expense_id = created['expense_id']

        success = self.expense_manager.update_receipt_url(
            expense_id, 'https://example.com/receipt.jpg'
        )

        self.assertTrue(success)
        updated = self.expense_manager.get_by_id(expense_id)
        self.assertEqual(updated['receipt_url'], 'https://example.com/receipt.jpg')

    def test_local_update_receipt_url_not_found(self):
        """Test updating receipt URL for non-existent expense fails"""
        success = self.expense_manager.update_receipt_url(
            99999, 'https://example.com/receipt.jpg'
        )

        self.assertFalse(success)

    def test_local_add_expense_with_receipt(self):
        """Test creating expense with receipt URL in local mode"""
        result = self.expense_manager.add_expense_with_receipt(
            user_id=self.user.id,
            amount=40.00,
            category='Dining',
            description='Dinner',
            receipt_url='https://example.com/receipt.jpg'
        )

        self.assertEqual(result['receipt_url'], 'https://example.com/receipt.jpg')
        self.assertEqual(result['amount'], 40.00)

    def test_local_add_expense_with_receipt_optional_url(self):
        """Test creating expense without receipt URL"""
        result = self.expense_manager.add_expense_with_receipt(
            user_id=self.user.id,
            amount=50.00,
            category='Shopping'
        )

        self.assertIsNone(result['receipt_url'])

    def test_local_get_by_user_empty(self):
        """Test getting expenses for user with no expenses"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

        expenses = self.expense_manager.get_by_user(other_user.id)

        self.assertEqual(len(expenses), 0)

    def test_local_expense_isolation(self):
        """Test expenses are isolated by user"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

        self.expense_manager.create(
            user_id=self.user.id,
            amount=10.00,
            category='Food'
        )
        self.expense_manager.create(
            user_id=other_user.id,
            amount=20.00,
            category='Transport'
        )

        self_expenses = self.expense_manager.get_by_user(self.user.id)
        other_expenses = self.expense_manager.get_by_user(other_user.id)

        self.assertEqual(len(self_expenses), 1)
        self.assertEqual(len(other_expenses), 1)
        self.assertEqual(self_expenses[0]['amount'], 10.00)
        self.assertEqual(other_expenses[0]['amount'], 20.00)


@override_settings(IS_LOCAL_DEMO=False)
class DynamoDBExpenseCloudTest(TestCase):
    """Test DynamoDBExpense in production mode (using DynamoDB)."""

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_create_expense(self, mock_get_table):
        """Test creating expense in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        result = expense_manager.create(
            user_id='user123',
            amount=25.50,
            category='Food',
            description='Lunch'
        )

        self.assertIn('expense_id', result)
        self.assertEqual(result['amount'], Decimal('25.50'))
        self.assertEqual(result['category'], 'Food')
        self.assertEqual(result['user_id'], 'user123')
        mock_table.put_item.assert_called_once()

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_get_by_user(self, mock_get_table):
        """Test retrieving expenses by user in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        mock_table.scan.return_value = {
            'Items': [
                {
                    'expense_id': 'exp1',
                    'user_id': 'user123',
                    'amount': Decimal('10.00'),
                    'category': 'Transport',
                    'timestamp': '2023-01-01T00:00:00'
                },
                {
                    'expense_id': 'exp2',
                    'user_id': 'user123',
                    'amount': Decimal('20.00'),
                    'category': 'Food',
                    'timestamp': '2023-01-02T00:00:00'
                }
            ]
        }

        expenses = expense_manager.get_by_user('user123')

        self.assertEqual(len(expenses), 2)
        self.assertEqual(expenses[0]['amount'], 10.00)
        mock_table.scan.assert_called_once()

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_get_by_id(self, mock_get_table):
        """Test retrieving specific expense in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        mock_table.get_item.return_value = {
            'Item': {
                'expense_id': 'exp1',
                'user_id': 'user123',
                'amount': Decimal('15.00'),
                'category': 'Entertainment'
            }
        }

        result = expense_manager.get_by_id('exp1')

        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 15.00)

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_get_by_id_not_found(self, mock_get_table):
        """Test retrieving non-existent expense in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        mock_table.get_item.return_value = {}

        result = expense_manager.get_by_id('non-existent')

        self.assertIsNone(result)

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_update_receipt_url(self, mock_get_table):
        """Test updating receipt URL in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        success = expense_manager.update_receipt_url(
            'exp1', 'https://example.com/receipt.jpg'
        )

        self.assertTrue(success)
        mock_table.update_item.assert_called_once()

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_update_receipt_url_error(self, mock_get_table):
        """Test updating receipt URL handles errors in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()
        mock_table.update_item.side_effect = Exception('DynamoDB error')

        success = expense_manager.update_receipt_url('exp1', 'url.jpg')

        self.assertFalse(success)

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_add_expense_with_receipt(self, mock_get_table):
        """Test creating expense with receipt in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        result = expense_manager.add_expense_with_receipt(
            user_id='user123',
            amount=40.00,
            category='Dining',
            description='Dinner',
            receipt_url='https://example.com/receipt.jpg'
        )

        self.assertEqual(result['receipt_url'], 'https://example.com/receipt.jpg')
        self.assertEqual(result['amount'], Decimal('40.00'))
        mock_table.put_item.assert_called_once()

    @patch('auth_app.models.get_dynamodb_table')
    def test_cloud_add_expense_without_receipt(self, mock_get_table):
        """Test creating expense without receipt in cloud mode"""
        mock_table = Mock()
        mock_get_table.return_value = mock_table
        expense_manager = DynamoDBExpense()

        result = expense_manager.add_expense_with_receipt(
            user_id='user123',
            amount=50.00,
            category='Shopping'
        )

        self.assertIsNone(result['receipt_url'])
        mock_table.put_item.assert_called_once()
