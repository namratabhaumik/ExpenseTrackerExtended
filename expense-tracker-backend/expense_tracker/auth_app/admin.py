from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import Expense


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date')
    search_fields = ('session_key',)
    readonly_fields = ('session_key', 'session_data', 'expire_date')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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
