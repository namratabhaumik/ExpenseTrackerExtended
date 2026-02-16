# Generated migration to add User ForeignKey with data migration

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_user_ids_to_foreign_key(apps, schema_editor):
    """Migrate existing user_id strings to User ForeignKey relationships."""
    Expense = apps.get_model('auth_app', 'Expense')
    User = apps.get_model('auth', 'User')

    deleted_count = 0
    migrated_count = 0

    for expense in Expense.objects.all():
        try:
            # Try to convert user_id string to integer and find matching User
            user_pk = int(expense.user_id)
            try:
                user = User.objects.get(pk=user_pk)
                expense.user = user
                expense.save(update_fields=['user'])
                migrated_count += 1
            except User.DoesNotExist:
                # No matching user found - delete this orphaned expense
                print(f"Warning: Deleting orphaned expense {expense.id} with user_id='{expense.user_id}' (user not found)")
                expense.delete()
                deleted_count += 1
        except (ValueError, TypeError):
            # user_id is not a valid integer string - delete this orphaned expense
            print(f"Warning: Deleting orphaned expense {expense.id} with invalid user_id='{expense.user_id}'")
            expense.delete()
            deleted_count += 1

    print(f"\nMigration summary:")
    print(f"  Migrated: {migrated_count} expenses to User ForeignKey")
    print(f"  Deleted: {deleted_count} orphaned expenses")


def reverse_migrate(apps, schema_editor):
    """Reverse migration - restore user_id from ForeignKey if possible."""
    Expense = apps.get_model('auth_app', 'Expense')

    for expense in Expense.objects.filter(user__isnull=False):
        expense.user_id = str(expense.user.id)
        expense.save(update_fields=['user_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # First remove the old CharField user_id
        migrations.RemoveField(
            model_name='expense',
            name='user_id',
        ),
        # Then add the ForeignKey (creates user_id column automatically)
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(help_text='User who created this expense', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL),
        ),
        # Run data migration to repopulate from old data
        migrations.RunPython(migrate_user_ids_to_foreign_key, reverse_migrate),
    ]
