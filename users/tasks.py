from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def check_inactive_users():
    """
    Check users who haven't logged in for more than a month
    and deactivate them.

    This task runs daily via celery-beat.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Find active users who haven't logged in for more than a month
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    )

    count = 0
    for user in inactive_users:
        user.is_active = False
        user.save(update_fields=['is_active'])
        count += 1

    return f'Deactivated {count} inactive users'