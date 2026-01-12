import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    # Check and block inactive users every day at midnight
    'check-inactive-users-daily': {
        'task': 'users.tasks.check_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
    # Send pending notifications every hour
    'send-pending-notifications-hourly': {
        'task': 'courses.tasks.send_pending_notifications',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour
    },
}

# Timezone configuration
app.conf.timezone = settings.TIME_ZONE


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery."""
    print(f'Request: {self.request!r}')