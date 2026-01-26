from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription, Lesson


@shared_task
def send_course_update_notification(course_id):
    """
    Send email notification to all subscribers about course update.

    Args:
        course_id: ID of the updated course
    """
    try:
        course = Course.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(
            course=course,
            is_active=True
        ).select_related('user')

        if not subscribers:
            return f'No active subscribers for course: {course.title}'

        subject = f'Обновление курса: {course.title}'
        message = (
            f'Уважаемый подписчик!\n\n'
            f'Курс "{course.title}" был обновлен.\n'
            f'Последнее обновление: {course.last_updated}\n\n'
            f'Описание курса: {course.description[:200]}...\n\n'
            f'Перейдите по ссылке для просмотра: '
            f'{settings.SITE_URL}/courses/{course.id}/\n\n'
            f'С уважением,\n'
            f'Команда LMS'
        )

        emails = [subscriber.user.email for subscriber in subscribers]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )

        return (
            f'Notification sent to {len(emails)} subscribers '
            f'for course: {course.title}'
        )

    except Course.DoesNotExist:
        return f'Course with id {course_id} does not exist'
    except Exception as e:
        return f'Error sending notifications: {str(e)}'


@shared_task
def send_lesson_update_notification(lesson_id):
    """
    Send email notification about lesson update.
    Only send if course wasn't updated in the last 4 hours.

    Args:
        lesson_id: ID of the updated lesson
    """
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        course = lesson.course

        # Check if course was updated in the last 4 hours
        four_hours_ago = timezone.now() - timedelta(hours=4)
        if course.last_updated > four_hours_ago:
            return (
                f'Course {course.title} was updated recently '
                f'(less than 4 hours ago). Skipping notification.'
            )

        subscribers = Subscription.objects.filter(
            course=course,
            is_active=True
        ).select_related('user')

        if not subscribers:
            return f'No active subscribers for lesson: {lesson.title}'

        subject = f'Обновлен урок в курсе: {course.title}'
        message = (
            f'Уважаемый подписчик!\n\n'
            f'В курсе "{course.title}" обновлен урок: {lesson.title}\n'
            f'Последнее обновление урока: {lesson.last_updated}\n\n'
            f'Описание урока: {lesson.description[:200]}...\n\n'
            f'Перейдите по ссылке для просмотра: '
            f'{settings.SITE_URL}/lessons/{lesson.id}/\n\n'
            f'С уважением,\n'
            f'Команда LMS'
        )

        emails = [subscriber.user.email for subscriber in subscribers]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )

        return (
            f'Lesson update notification sent to {len(emails)} subscribers '
            f'for lesson: {lesson.title}'
        )

    except Lesson.DoesNotExist:
        return f'Lesson with id {lesson_id} does not exist'
    except Exception as e:
        return f'Error sending notifications: {str(e)}'


@shared_task
def send_pending_notifications():
    """
    Send pending notifications for recently updated courses and lessons.
    This task runs periodically via celery-beat.
    """
    # Find courses updated in the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recently_updated_courses = Course.objects.filter(
        last_updated__gte=one_hour_ago
    )

    results = []
    for course in recently_updated_courses:
        result = send_course_update_notification.delay(course.id)
        results.append(f'Course {course.title}: {result}')

    return f'Sent notifications for {len(results)} courses'


# Add SITE_URL to settings if not exists
if not hasattr(settings, 'SITE_URL'):
    settings.SITE_URL = 'http://localhost:8000'