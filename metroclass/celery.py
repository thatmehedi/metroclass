import os

try:
    from celery import Celery
    from celery.schedules import crontab

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metroclass.settings')

    app = Celery('metroclass')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()

    # Schedule: checks deadlines every hour automatically
    app.conf.beat_schedule = {
        'check-deadlines-every-hour': {
            'task': 'notifications.tasks.check_deadline_reminders_task',
            'schedule': crontab(minute=0),
        },
    }
except ImportError:
    app = None
