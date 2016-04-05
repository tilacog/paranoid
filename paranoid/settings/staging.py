from .base import *


DEBUG = True
DOMAIN = 'staging.paranoidlabs.com.br'
ALLOWED_HOSTS = [DOMAIN]
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CELERY
BROKER_URL += '/staging'