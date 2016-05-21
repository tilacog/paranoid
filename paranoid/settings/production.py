from .base import *


DEBUG = False
DOMAIN = 'spedauditor.com.br'
ALLOWED_HOSTS = [DOMAIN]

# CELERY
BROKER_URL += '/main'

# MAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST= config.get('mail', 'EMAIL_HOST')
EMAIL_PORT = config.getint('mail', 'EMAIL_PORT')
EMAIL_HOST_USER=config.get('mail', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('mail', 'EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config.getboolean('mail', 'EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = config.get('mail', 'DEFAULT_FROM_EMAIL')
