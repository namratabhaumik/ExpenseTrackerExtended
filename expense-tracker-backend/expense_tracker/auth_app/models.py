from django.db import models

# The DynamoDBExpense logic has been moved to services/DynamoDBExpenseService.py

# Legacy Django model - deprecated in favor of DynamoDB
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
