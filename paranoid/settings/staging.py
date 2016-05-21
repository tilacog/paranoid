from .base import *


DEBUG = True
DOMAIN = 'staging.spedauditor.com.br'
ALLOWED_HOSTS = [DOMAIN]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# CELERY
BROKER_URL += '/staging'
