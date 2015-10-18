"""
Django settings for paranoid project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# Test-specific configs
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&*j6py4zmaemppv%#q1tf@&*ii1@riw41#*3i)7qjz1&r2(e+s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

AUTH_USER_MODEL = 'accounts.ParanoidUser'
AUTHENTICATION_BACKENDS = (
    'accounts.authentication.ParanoidAuthenticationBackend',
)


# This setting is changed by the deploy script
DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]


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
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

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
            'filename': 'paranoid.log',
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
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp'
