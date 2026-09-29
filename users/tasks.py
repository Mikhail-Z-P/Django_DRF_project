from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import User


@shared_task
def deactivate_inactive_users():
    """Блокирует пользователей, не входивших более месяца."""
    threshold = timezone.now() - timedelta(days=30)
    count = User.objects.filter(
        last_login__lt=threshold,
        is_active=True,
    ).update(is_active=False)
    return f"Деактивировано пользователей: {count}"
