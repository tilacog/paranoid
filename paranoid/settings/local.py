from .base import *

DEBUG = True

DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]

# CELERY SETTINGS
# TODO: Put rabbitmq settings under a secret config file
# TODO: Create a user with password to use rabbitmq
BROKER_URL = 'amqp://guest@localhost:5672//main'

# SECURITY WARNING: keep the secret key used in production secret!
#TODO: Put secret key under a sectret config file
SECRET_KEY = '&*j6py4zmaemppv%#q1tf@&*ii1@riw41#*3i)7qjz1&r2(e+s'
