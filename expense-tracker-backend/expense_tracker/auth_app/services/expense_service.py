"""Abstract expense repository interface and factory."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from django.conf import settings


class ExpenseRepository(ABC):
    """Abstract interface for expense storage operations."""

    @abstractmethod
    def create(
        self, user_id: int, amount: float, category: str, description: str = ""
    ) -> Dict:
        """
        Create a new expense.

        Returns:
            Dictionary with expense_id, user_id, amount, category, description, timestamp, receipt_url
        """
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Dict]:
        """
        Get all expenses for a user.

        Returns:
            List of expense dictionaries
        """
        pass

    @abstractmethod
    def get_by_id(self, expense_id: str) -> Optional[Dict]:
        """
        Get a specific expense by ID.

        Returns:
            Expense dictionary or None if not found
        """
        pass

    @abstractmethod
    def update_receipt_url(self, expense_id: str, receipt_url: str) -> bool:
        """
        Link a receipt URL to an expense.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def add_expense_with_receipt(
        self,
        user_id: int,
        amount: float,
        category: str,
        description: str = "",
        receipt_url: Optional[str] = None,
    ) -> Dict:
        """
        Create an expense with optional receipt URL.

        Returns:
            Dictionary with complete expense data
        """
        pass


def get_expense_repository() -> ExpenseRepository:
    """
    Factory function to get appropriate expense repository based on environment.

    Returns:
        SQLiteExpenseRepository if IS_LOCAL_DEMO=true, else DynamoDBExpenseRepository
    """
    is_local_demo = settings.IS_LOCAL_DEMO if hasattr(settings, 'IS_LOCAL_DEMO') else False

    if is_local_demo:
        from local_app.implementations.sqlite_expense_repo import (
            SQLiteExpenseRepository,
        )
        return SQLiteExpenseRepository()
    else:
        from cloud_app.implementations.dynamodb_expense_repo import (
            DynamoDBExpenseRepository,
        )
        return DynamoDBExpenseRepository()
