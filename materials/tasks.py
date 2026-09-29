from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """Отправляет email подписчикам курса об обновлении материалов."""
    course = Course.objects.get(pk=course_id)
    subscriptions = Subscription.objects.filter(course=course)
    emails = [sub.user.email for sub in subscriptions if sub.user.email]
    if not emails:
        return
    send_mail(
        subject="Курс обновлён",
        message=f'Материалы курса "{course.title}" были обновлены.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
