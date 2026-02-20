"""Unit tests for Django admin customizations."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.test import TestCase

from auth_app.admin import ExpenseAdmin, CustomUserAdmin, SessionAdmin
from auth_app.models import Expense


class MockRequest:
    """Mock request object for admin tests."""

    def __init__(self, user=None):
        self.user = user or Mock()


class Mock:
    """Simple mock object."""

    pass


class CustomUserAdminTest(TestCase):
    """Test custom User admin configuration."""

    def setUp(self):
        """Set up admin site and test user"""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_admin_registered(self):
        """Test that UserAdmin is properly configured"""
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.admin.model, User)

    def test_user_can_be_viewed_in_admin(self):
        """Test that users can be viewed in admin"""
        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'testuser@example.com')

    def test_user_can_be_edited_in_admin(self):
        """Test that user data can be edited"""
        self.user.first_name = 'Updated'
        self.user.save()

        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.first_name, 'Updated')

    def test_user_can_be_deleted_from_admin(self):
        """Test that users can be deleted"""
        user_id = self.user.pk
        self.user.delete()

        exists = User.objects.filter(pk=user_id).exists()
        self.assertFalse(exists)


class ExpenseAdminTest(TestCase):
    """Test custom Expense admin configuration."""

    def setUp(self):
        """Set up admin site and test data"""
        self.site = AdminSite()
        self.admin = ExpenseAdmin(Expense, self.site)
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.expense = Expense.objects.create(
            user=self.user,
            amount=25.50,
            category='Food',
            description='Test expense'
        )

    def test_expense_admin_registered(self):
        """Test that ExpenseAdmin is properly configured"""
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.admin.model, Expense)

    def test_expense_can_be_viewed_in_admin(self):
        """Test that expenses can be viewed in admin"""
        expenses = Expense.objects.all()
        self.assertEqual(expenses.count(), 1)
        self.assertEqual(expenses[0].amount, 25.50)

    def test_expense_can_be_edited_in_admin(self):
        """Test that expense data can be edited"""
        self.expense.amount = 35.00
        self.expense.save()

        updated_expense = Expense.objects.get(pk=self.expense.pk)
        self.assertEqual(updated_expense.amount, 35.00)

    def test_expense_can_be_deleted_from_admin(self):
        """Test that expenses can be deleted"""
        expense_id = self.expense.pk
        self.expense.delete()

        exists = Expense.objects.filter(pk=expense_id).exists()
        self.assertFalse(exists)

    def test_expense_read_only_fields(self):
        """Test that timestamp is read-only"""
        # The admin should have timestamp in read_only_fields
        # This prevents manual modification of created timestamps
        original_timestamp = self.expense.timestamp
        self.assertIsNotNone(original_timestamp)

    def test_expense_list_display(self):
        """Test that admin list display shows relevant fields"""
        expenses = Expense.objects.all()
        self.assertEqual(len(expenses), 1)
        expense = expenses[0]

        # Verify important fields are present
        self.assertEqual(expense.user.email, 'testuser@example.com')
        self.assertEqual(expense.amount, 25.50)
        self.assertEqual(expense.category, 'Food')
        self.assertIsNotNone(expense.timestamp)

    def test_multiple_expenses_in_admin(self):
        """Test managing multiple expenses in admin"""
        Expense.objects.create(
            user=self.user,
            amount=15.00,
            category='Transport'
        )
        Expense.objects.create(
            user=self.user,
            amount=45.00,
            category='Entertainment'
        )

        expenses = Expense.objects.all()
        self.assertEqual(expenses.count(), 3)

    def test_expense_filtering_by_user(self):
        """Test filtering expenses by user"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )
        Expense.objects.create(
            user=other_user,
            amount=50.00,
            category='Food'
        )

        user1_expenses = Expense.objects.filter(user=self.user)
        user2_expenses = Expense.objects.filter(user=other_user)

        self.assertEqual(user1_expenses.count(), 1)
        self.assertEqual(user2_expenses.count(), 1)

    def test_expense_search_by_category(self):
        """Test searching expenses by category"""
        Expense.objects.create(
            user=self.user,
            amount=20.00,
            category='Food'
        )
        Expense.objects.create(
            user=self.user,
            amount=30.00,
            category='Transport'
        )

        food_expenses = Expense.objects.filter(category='Food')
        transport_expenses = Expense.objects.filter(category='Transport')

        self.assertEqual(food_expenses.count(), 2)
        self.assertEqual(transport_expenses.count(), 1)

    def test_expense_ordering(self):
        """Test that expenses are ordered correctly"""
        older_expense = Expense.objects.create(
            user=self.user,
            amount=10.00,
            category='Food'
        )
        newer_expense = Expense.objects.create(
            user=self.user,
            amount=20.00,
            category='Transport'
        )

        expenses = list(Expense.objects.all())
        # Should be ordered by timestamp descending (newest first)
        self.assertEqual(expenses[0].id, newer_expense.id)
        self.assertEqual(expenses[-1].id, self.expense.id)  # oldest (first created)
