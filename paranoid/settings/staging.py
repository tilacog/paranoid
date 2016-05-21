from .base import *


DEBUG = True
DOMAIN = 'staging.paranoidlabs.com.br'
ALLOWED_HOSTS = [DOMAIN, 'staging.spedauditor.com.br']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# CELERY
BROKER_URL += '/staging'
