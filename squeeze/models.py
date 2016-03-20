import random
import string

from django.db import models

def random_key():
    """A random string for uniquely identify the squeeze page jobs.
    """
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(40)
    )


class SqueezeJob(models.Model):
    """A job who came from the squeeze page."""
    job = models.ForeignKey('jobs.Job',)
    real_user_email = models.EmailField()
    created_on = models.DateTimeField(auto_now_add=True)
    notified_on = models.DateTimeField(blank=True, null=True)
    random_key = models.CharField(max_length=40, default=random_key)
