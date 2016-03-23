from celery import group, shared_task, task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from jobs.models import Job
from squeeze.models import SqueezeJob

MAIL_MESSAGES = {
        'SUCCESS_SUBJECT': 'Sua análise SPED está pronta!',
        'SUCCESS_TEMPLATE': 'success_email_body.html',
        'FAILURE_SUBJECT': '',
        'FAILURE_TEMPLATE': '',
}

@task
def notify_beta_users():
    qs = SqueezeJob.objects.filter(notified_at='')
    for squeezejob in qs:
        # Update notification timestamp
        squeezejob.notified_at = timezone.now()
        squeezejob.save()

        html_message = render_to_string(
            template_name=MAIL_MESSAGES['SUCCESS_TEMPLATE'],
            context={'squeezejob': squeezejob},
        )

        send_mail(
            to=[squeezejob.real_user_email],
            subject=MAIL_MESSAGES['SUCCESS_SUBJECT'],
            html_message=html_message,
        )
