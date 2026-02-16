from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.sessions.models import Session
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Expense


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Session admin with user information display."""

    list_display = ('session_key', 'get_user_email', 'get_user_id', 'expire_date', 'is_active')
    search_fields = ('session_key',)
    readonly_fields = ('session_key', 'session_data', 'expire_date', 'get_decoded_session')
    list_filter = ('expire_date',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_user_email(self, obj):
        """Extract and display user email from session data."""
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')

            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    url = f"/admin/auth/user/{user.id}/change/"
                    return format_html(
                        '<a href="{}">{}</a>',
                        url,
                        user.email or user.username,
                    )
                except User.DoesNotExist:
                    return "(deleted)"
            return "-"
        except Exception:
            return "Unable to decode"

    get_user_email.short_description = 'User Email'

    def get_user_id(self, obj):
        """Extract and display user ID from session data."""
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')

            if user_id:
                return user_id
            return "-"
        except Exception:
            return "Unable to decode"

    get_user_id.short_description = 'User ID'

    def is_active(self, obj):
        """Show if session is currently active."""
        from django.utils import timezone
        is_active_session = obj.expire_date > timezone.now()
        color = 'green' if is_active_session else 'red'
        text = 'Active' if is_active_session else 'Expired'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )

    is_active.short_description = 'Status'

    def get_decoded_session(self, obj):
        """Show decoded session data in readable format."""
        try:
            session_data = obj.get_decoded()
            formatted = "<br>".join(
                f"<strong>{k}:</strong> {v}" for k, v in session_data.items()
            )
            return mark_safe(formatted)
        except Exception as e:
            return f"Error decoding: {str(e)}"

    get_decoded_session.short_description = 'Decoded Session Data'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    """Custom User admin that displays the ID field."""

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('id', 'username', 'email')
    ordering = ('-date_joined',)
    readonly_fields = DefaultUserAdmin.readonly_fields + ('id',)

    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Expense admin with user relationship display."""

    list_display = (
        'id',
        'get_user_display',
        'get_user_id',
        'amount',
        'category',
        'description_preview',
        'timestamp',
        'has_receipt'
    )
    list_filter = ('category', 'timestamp', 'user')
    search_fields = (
        'user__username',
        'user__email',
        'category',
        'description',
    )
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'id')
    list_select_related = ('user',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
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

    def get_user_display(self, obj):
        """Display user email with link to user admin."""
        if obj.user:
            url = f"/admin/auth/user/{obj.user.id}/change/"
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.user.email or obj.user.username,
            )
        return "No user"

    get_user_display.short_description = 'User Email'
    get_user_display.admin_order_field = 'user__email'

    def get_user_id(self, obj):
        """Display user ID in a separate column."""
        if obj.user:
            return obj.user.id
        return '-'

    get_user_id.short_description = 'User ID'
    get_user_id.admin_order_field = 'user_id'

    def description_preview(self, obj):
        """Show truncated description."""
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return '-'

    description_preview.short_description = 'Description'

    def has_receipt(self, obj):
        """Show if expense has receipt attached."""
        if obj.receipt_url:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Yes</span>'
            )
        return format_html(
            '<span style="color: gray;">-</span>'
        )

    has_receipt.short_description = 'Receipt'
    has_receipt.admin_order_field = 'receipt_url'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')
