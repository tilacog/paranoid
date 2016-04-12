"""
Django settings for paranoid project.
"""

import configparser
import logging
import sys
from datetime import timedelta

import unipath

logger = logging.getLogger(__name__)

# PATHS
THIS_DIR = unipath.Path(__file__).parent
BASE_DIR = THIS_DIR.ancestor(2)

# Config parser
config = configparser.ConfigParser()
config.read(THIS_DIR.child('secrets.ini'))

# CELERY SETTINGS
CELERY_RESULT_BACKEND = 'amqp'
BROKER_URL = config.get('celery', 'BROKER_URL')
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = True

CELERYBEAT_SCHEDULE = {
    'notify-beta-users': {
        'task': 'squeeze.tasks.notify_beta_users',
        'schedule': timedelta(seconds=30),
    },
    'delete_expired_files': {
        'task': 'squeeze.tasks.notify_beta_users',
        'schedule': timedelta(hours=12),
    },
}

# TRACKING
GOOGLE_ANALYTICS_PROPERTY_ID = config.get(
    'tracking',
    'GOOGLE_ANALYTICS_PROPERTY_ID',
)

# DJANGO
SECRET_KEY = config.get('django', 'SECRET_KEY', raw=True)
ADMINS = [config.get('django', 'ADMINS')]

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
    'widget_tweaks',
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
        'NAME': BASE_DIR.parent.child('database', 'db.sqlite3'),
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
STATIC_ROOT = BASE_DIR.parent.child('static')
STATICFILES_DIRS = (
    BASE_DIR.child('paranoid', 'static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent.child('media')

# Home for finished report files
# TODO: Refactor: http://stackoverflow.com/q/9446897/1288794
FINISHED_REPORTS = MEDIA_ROOT.child('reports')

# MAIL
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# More detailed logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(process)d'
                       '%(thread)d %(message)s')
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

# Add external plugins directory to PATH as a namespace package under "runner"
# module
PLUGINS_PATH = BASE_DIR.parent.child('plugins').absolute()
sys.path.extend([PLUGINS_PATH, '.'])

# TODO: Move plugin import logic to the runner.app module
# Load external plugins
try:
    from runner.plugins import load_plugins
    load_plugins()
except ImportError as e:
    logger.warning('Could not import external plugins. ({})'.format(e))

# Load local plugins
import runner.plugins_local  # noqa
