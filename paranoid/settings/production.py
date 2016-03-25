from .base import *

DEBUG = False

DOMAIN = "paranoidlabs.com.br"
ALLOWED_HOSTS = [DOMAIN]

# CELERY SETTINGS
BROKER_URL = 'amqp://'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&*j6py4zmaemppv%#q1tf@&*ii1@riw41#*3i)7qjz1&r2(e+s'
