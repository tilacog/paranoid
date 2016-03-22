from celery import group, shared_task, task
from django.core.mail import send_mail

from squeeze.models import SqueezeJob
from jobs.models import Job

MAIL_MESSAGES = {
        'SUCCESS_SUBJECT': '',
        'SUCCESS_TEXT_TEMPLATE': '',
        'FAILURE_SUBJECT': '',
        'FAILURE_TEXT_TEMPLATE': '',
}

@task
def notify_beta_users():
    pass
