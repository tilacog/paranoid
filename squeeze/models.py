import random
import string

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now, timedelta

def random_key():
    """A random string for uniquely identify the squeeze page jobs.
    """
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(40)
    )


class SqueezeJob(models.Model):
    """A job who came from the squeeze page.
    """

    DEFAULT_TIMEOUT = timedelta(days=3)

    job = models.ForeignKey('jobs.Job',)
    real_user_email = models.EmailField()
    real_user_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(blank=True, null=True)
    random_key = models.CharField(max_length=40, default=random_key)

    @property
    def download_link(self):
        return reverse('download_squeezejob', args=[self.random_key])

    @property
    def absolute_download_link(self):
        return 'http://' + settings.DOMAIN + self.download_link

    @property
    def is_expired(self):
        return now() > self.created_at + self.DEFAULT_TIMEOUT
