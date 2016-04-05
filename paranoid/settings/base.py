"""
Django settings for paranoid project.
"""

import configparser
import logging
import os
import sys
from datetime import timedelta


logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

config =  configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'secrets.ini'))

SECRET_KEY =  config.get('django', 'SECRET_KEY', raw=True)

# CELERY SETTINGS
CELERY_RESULT_BACKEND = 'amqp'
BROKER_URL = config.get('celery', 'BROKER_URL')
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = True

# TRACKING
GOOGLE_ANALYTICS_PROPERTY_ID = config.get(
    'tracking',
    'GOOGLE_ANALYTICS_PROPERTY_ID',
    fallback=None
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'squeeze.context_processors.google_analytics',
            ],
        },
    },
]

AUTH_USER_MODEL = 'accounts.ParanoidUser'
AUTHENTICATION_BACKENDS = (
    'accounts.authentication.ParanoidAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'audits',
    'functional_tests',
    'jobs',
    'squeeze',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'paranoid.urls'

WSGI_APPLICATION = 'paranoid.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../database/db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'paranoid', 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
MEDIA_URL = '/media/'

# Home for finished report files
FINISHED_REPORTS = os.path.join(MEDIA_ROOT, 'reports')


# More detailed logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'site_logfile.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
        },
        'accounts': {
            'handlers': ['console', 'file'],
        },
        'jobs': {
            'handlers': ['console', 'file'],
        },
    },
    'root': {'level': 'INFO'},
}


# Test specific settings
if 'test' in sys.argv:
    # Ignore naive datetime warning from IPython
    import warnings
    warnings.filterwarnings(
        "ignore",
        category=RuntimeWarning,
        module='django.db.backends.sqlite3.base',
        lineno=53
    )


CELERYBEAT_SCHEDULE = {
    'notify-beta-users': {
        'task': 'squeeze.tasks.notify_beta_users',
        'schedule': timedelta(seconds=30),
    },
}

# Add external plugins directory to PATH as a namespace package under "runner"
# module
PLUGINS_PATH = os.path.abspath(
    os.path.join(BASE_DIR, '../plugins')
)
sys.path.extend([PLUGINS_PATH, '.'])

#TODO: Move plugin import logic to the runner.app module
# Load external plugins
try:
    from runner.plugins import load_plugins
    load_plugins()
except ImportError as e:
    logger.warning('Could not import external plugins. ({})'.format(e))

# Load local plugins
import runner.plugins_local


# Settings for sending email with Postfix
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'Contato Titan <titan@paranoidlabs.com.br>'
