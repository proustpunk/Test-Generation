import os
from celery import Celery

from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ResumeScreening.settings')

app = Celery('ResumeScreening')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.timezone = 'Asia/Kathmandu'
app.conf.enable_utc = True
