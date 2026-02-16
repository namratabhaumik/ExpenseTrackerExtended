"""SQLite expense repository implementation for local development."""

import logging
from typing import Dict, List, Optional

from django.contrib.auth.models import User

from auth_app.models import Expense
from auth_app.services.expense_service import ExpenseRepository

logger = logging.getLogger(__name__)


class SQLiteExpenseRepository(ExpenseRepository):
    """Expense storage using Django ORM with SQLite and proper User relationships."""

    def create(
        self, user_id: int, amount: float, category: str, description: str = ''
    ) -> Dict:
        """Create a new expense in SQLite using User ForeignKey."""
        try:
            user = User.objects.get(pk=user_id)
            expense = Expense.objects.create(
                user=user,
                amount=amount,
                category=category,
                description=description,
            )

            logger.info(f'Expense created: {expense.id} for user: {user_id}')

            return {
                'expense_id': str(expense.id),
                'user_id': expense.user.id,
                'amount': float(expense.amount),
                'category': expense.category,
                'description': expense.description,
                'timestamp': expense.timestamp.isoformat(),
                'receipt_url': expense.receipt_url,
            }

        except User.DoesNotExist:
            logger.error(f'User not found: {user_id}')
            raise ValueError(f'User with id {user_id} does not exist')
        except Exception as e:
            logger.error(f'Error creating expense: {str(e)}', exc_info=True)
            raise

    def get_by_user(self, user_id: int) -> List[Dict]:
        """Get all expenses for a user from SQLite using ForeignKey with optimization."""
        try:
            expenses = Expense.objects.filter(
                user_id=user_id
            ).select_related('user').order_by('-timestamp')

            result = [
                {
                    'expense_id': str(exp.id),
                    'user_id': exp.user.id,
                    'amount': float(exp.amount),
                    'category': exp.category,
                    'description': exp.description,
                    'timestamp': exp.timestamp.isoformat(),
                    'receipt_url': exp.receipt_url,
                }
                for exp in expenses
            ]

            logger.info(f'Retrieved {len(result)} expenses for user: {user_id}')
            return result

        except Exception as e:
            logger.error(f'Error retrieving expenses for user {user_id}: {str(e)}', exc_info=True)
            raise

    def get_by_id(self, expense_id: str) -> Optional[Dict]:
        """Get a specific expense by ID from SQLite."""
        try:
            expense = Expense.objects.select_related('user').get(id=expense_id)

            logger.info(f'Retrieved expense: {expense_id}')

            return {
                'expense_id': str(expense.id),
                'user_id': expense.user.id if expense.user else None,
                'amount': float(expense.amount),
                'category': expense.category,
                'description': expense.description,
                'timestamp': expense.timestamp.isoformat(),
                'receipt_url': expense.receipt_url,
            }

        except Expense.DoesNotExist:
            logger.warning(f'Expense not found: {expense_id}')
            return None
        except Exception as e:
            logger.error(f'Error retrieving expense {expense_id}: {str(e)}', exc_info=True)
            raise

    def update_receipt_url(self, expense_id: str, receipt_url: str) -> bool:
        """Update an expense with a receipt URL."""
        try:
            expense = Expense.objects.get(id=expense_id)
            expense.receipt_url = receipt_url
            expense.save()

            logger.info(f'Receipt URL updated for expense: {expense_id}')
            return True

        except Expense.DoesNotExist:
            logger.warning(f'Expense not found: {expense_id}')
            return False
        except Exception as e:
            logger.error(f'Error updating receipt URL for {expense_id}: {str(e)}', exc_info=True)
            return False

    def add_expense_with_receipt(
        self,
        user_id: int,
        amount: float,
        category: str,
        description: str = '',
        receipt_url: Optional[str] = None,
    ) -> Dict:
        """Create a new expense with optional receipt URL using User ForeignKey."""
        try:
            user = User.objects.get(pk=user_id)
            expense = Expense.objects.create(
                user=user,
                amount=amount,
                category=category,
                description=description,
                receipt_url=receipt_url,
            )

            logger.info(f'Expense with receipt created: {expense.id} for user: {user_id}')

            return {
                'expense_id': str(expense.id),
                'user_id': expense.user.id,
                'amount': float(expense.amount),
                'category': expense.category,
                'description': expense.description,
                'timestamp': expense.timestamp.isoformat(),
                'receipt_url': expense.receipt_url,
            }

        except User.DoesNotExist:
            logger.error(f'User not found: {user_id}')
            raise ValueError(f'User with id {user_id} does not exist')
        except Exception as e:
            logger.error(
                f'Error creating expense with receipt for user {user_id}: {str(e)}',
                exc_info=True,
            )
            raise
