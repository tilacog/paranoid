from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

def report_filename(instance, filename):
    return '/'.join(['reports', instance.user.email, filename])


class Job(models.Model):

    RECEIVED_STATE = 1
    STARTED_STATE = 2
    SUCCESS_STATE = 3
    FAILURE_STATE = 4

    STATE_CHOICES = (
        (RECEIVED_STATE, 'Recebido'),
        (STARTED_STATE, 'Em processamento'),
        (SUCCESS_STATE, 'Concluído'),
        (FAILURE_STATE, 'Erro'),
    )

    audit = models.ForeignKey('audits.Audit')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    documents = models.ManyToManyField('audits.Document')
    state = models.IntegerField(choices=STATE_CHOICES, default=RECEIVED_STATE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_file = models.FileField(upload_to=report_filename, blank=True)

    def get_absolute_url(self):
        return reverse('new_job', args=[self.pk])

    def __repr__(self):
        return "<Job: pk={}>".format(self.pk)

    def add_report(self, report_file):
        """Add report file and update job state"""
        self.report_file = report_file
        self.state = Job.SUCCESS_STATE
        self.full_clean()
        self.save()
