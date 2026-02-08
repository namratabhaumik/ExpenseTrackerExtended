from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'amount', 'category', 'description', 'timestamp', 'receipt_url')
    list_filter = ('category', 'timestamp', 'user_id')
    search_fields = ('user_id', 'category', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'id')

    fieldsets = (
        ('User Info', {
            'fields': ('user_id',)
        }),
        ('Expense Details', {
            'fields': ('amount', 'category', 'description')
        }),
        ('File Attachment', {
            'fields': ('receipt_url',)
        }),
        ('Metadata', {
            'fields': ('timestamp', 'id'),
            'classes': ('collapse',)
        }),
    )
