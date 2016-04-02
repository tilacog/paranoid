from .base import *


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEBUG = True
SECRET_KEY =  config.get('django', 'SECRET_KEY', raw=True)
ALLOWED_HOSTS = 'localhost'

# CELERY SETTINGS
BROKER_URL = config.get('celery', 'BROKER_URL')
CELERY_RESULT_BACKEND = config.get('celery', 'CELERY_RESULT_BACKEND')
CELERY_TASK_SERIALIZER = config.get('celery', 'CELERY_TASK_SERIALIZER')

GOOGLE_ANALYTICS_PROPERTY_ID = config.get(
    'tracking',
    'GOOGLE_ANALYTICS_PROPERTY_ID'
)
