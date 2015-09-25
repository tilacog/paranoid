from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models


class Job(models.Model):
    audit = models.ForeignKey('audits.Audit')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    documents = models.ManyToManyField('audits.Document')

    def get_absolute_url(self):
        return reverse('new_job', args=[self.pk])
