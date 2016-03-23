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
        'FAILURE_TEMPLATE': 'failure_email_body.html',
}

@task
def notify_beta_users():
    qs = SqueezeJob.objects.filter(notified_at='')
    for squeezejob in qs:
        # Update notification timestamp
        squeezejob.notified_at = timezone.now()
        squeezejob.save()

        if squeezejob.job.state == Job.SUCCESS_STATE:
            template = 'SUCCESS_TEMPLATE'
            subject = 'SUCCESS_SUBJECT'

        elif squeezejob.job.state == Job.FAILURE_STATE:
            template = 'FAILURE_TEMPLATE'
            subject = 'FAILURE_SUBJECT'

        else:
            return

        # Build message
        html_message = render_to_string(
            template_name=MAIL_MESSAGES[template],
            context={'squeezejob': squeezejob},
        )

        # Dispatch mail
        send_mail(
            to=[squeezejob.real_user_email],
            subject=MAIL_MESSAGES[subject],
            html_message=html_message,
        )
