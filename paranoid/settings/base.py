"""
Django settings for paranoid project.
"""

import os
import sys
import logging


logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

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
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'site_logfile.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'accounts': {
            'handlers': ['console'],
        },
        'jobs': {
            'handlers': ['console'],
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

# CELERY SETTINGS
BROKER_URL = 'amqp://'  # TODO: Put broker url on supervisord.conf file

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
