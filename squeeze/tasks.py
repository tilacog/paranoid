from celery import group, shared_task, task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from jobs.models import Job
from squeeze.models import SqueezeJob

logger = get_task_logger(__name__)


MAIL_MESSAGES = {
        'SUCCESS_SUBJECT': 'Seu aqruivo SPED foi convertido com sucesso',
        'SUCCESS_TEXT_TEMPLATE': 'success_email_body.txt',
        'SUCCESS_HTML_TEMPLATE': 'success_email_body.html',
        'FAILURE_SUBJECT': 'Não conseguimos converter seu arquivo',
        'FAILURE_TEXT_TEMPLATE': 'failure_email_body.txt',
        'FAILURE_HTML_TEMPLATE': 'failure_email_body.html',
}

def build_messages(state, context):
    """Build and return a text and an html message.
    The state argument must be either "success" or "failure".
    """

    assert state in ('failure', 'success')

    if state == 'success':
        templates = ('SUCCESS_HTML_TEMPLATE', 'SUCCESS_TEXT_TEMPLATE')
    elif state == 'failure':
        templates = ('FAILURE_HTML_TEMPLATE', 'FAILURE_TEXT_TEMPLATE')

    text_message = render_to_string(
        template_name=MAIL_MESSAGES[templates[0]],
        context=context,
    )

    html_message = render_to_string(
        template_name=MAIL_MESSAGES[templates[1]],
        context=context,
    )

    return (text_message, html_message)


@task
def notify_beta_users():
    qs = SqueezeJob.objects.filter(notified_at__isnull=True)
    for squeezejob in qs:
        # Update notification timestamp
        squeezejob.notified_at = timezone.now()
        squeezejob.save()

        if squeezejob.job.state == Job.SUCCESS_STATE:
            subject = 'SUCCESS_SUBJECT'
            state = 'success'

        elif squeezejob.job.state == Job.FAILURE_STATE:
            subject = 'FAILURE_SUBJECT'
            state = 'failure'

        else:
            return

        # Build messages
        text_message, html_message = build_messages(
            state, context={'squeezejob': squeezejob}
        )


        logger.info('Sending squeezejob {} mail to {}.'.format(
            state,
            squeezejob.real_user_email
        ))

        # Dispatch mail
        send_mail(
            message=text_message,
            recipient_list=[squeezejob.real_user_email],
            subject=MAIL_MESSAGES[subject],
            html_message=html_message,
            from_email='titan@paranoidlabs.com.br',
        )
