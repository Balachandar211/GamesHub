import os
from celery import Celery, Task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GamesHub.settings')

app = Celery('GamesHub')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

import django
django.setup()

import utills.batches


