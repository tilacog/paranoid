from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils import timezone

from jobs.models import Job
from squeeze.models import SqueezeJob


logger = get_task_logger(__name__)

SQUEEZE_PAGE_URL= 'http://' + settings.DOMAIN + reverse('squeeze_page')
ADMINS = settings.ADMINS
MAIL_MESSAGES = {
    'SUCCESS_SUBJECT': 'Seu arquivo SPED foi convertido com sucesso',
    'SUCCESS_TEXT_TEMPLATE': 'success-email-body.txt',
    'SUCCESS_HTML_TEMPLATE': 'success-email-body.html',
    'FAILURE_SUBJECT': 'Não conseguimos converter seu arquivo',
    'FAILURE_TEXT_TEMPLATE': 'failure-email-body.txt',
    'FAILURE_HTML_TEMPLATE': 'failure-email-body.html',
}


def build_messages(state, context):
    """Build and return a text and an html message.
    The state argument must be either "success" or "failure".
    """

    assert state in ('failure', 'success')

    if state == 'success':
        templates = ('SUCCESS_TEXT_TEMPLATE', 'SUCCESS_HTML_TEMPLATE')
    elif state == 'failure':
        templates = ('FAILURE_TEXT_TEMPLATE', 'FAILURE_HTML_TEMPLATE')

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
            state,
            context={
                'squeezejob': squeezejob,
                'squeeze_page_url': SQUEEZE_PAGE_URL,
            }
        )

        logger.info('Sending squeezejob {} mail to {}.'.format(
            state,
            squeezejob.real_user_email
        ))

        # Dispatch mail
        msg = EmailMultiAlternatives(
            subject=MAIL_MESSAGES[subject],
            body=text_message,
            to=[squeezejob.real_user_email],
            bcc=ADMINS,
            from_email='Conversor Excel <conversor-excel@paranoidlabs.com.br>',
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()


@task
def delete_expired_files():
    date_limit = timezone.now() - SqueezeJob.DEFAULT_TIMEOUT


    expired_squeezejobs = SqueezeJob.objects.filter(created_at__lte=date_limit)
    for squeezejob in expired_squeezejobs:
            for document in squeezejob.job.documents.all():
                document.file.delete()
            squeezejob.job.report_file.delete()
            squeezejob.save()
