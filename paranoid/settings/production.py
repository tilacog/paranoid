from .base import *


DEBUG = False
ALLOWED_HOSTS = 'paranoidlabs.com.br'

# MAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = config.get('mail','EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('mail', 'EMAIL_HOST_PASSWORD')
