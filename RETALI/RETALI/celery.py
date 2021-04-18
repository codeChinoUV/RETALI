""""
Autor: José Miguel Quiroz Benitez
Fecha de creación: 22/03/2021
Ultima actualización: 22/03/2021
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RETALI.settings')

celery_app = Celery('RETALI')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
