from django.db.models.signals import post_save
from django.dispatch import receiver

from jobs.models import Job


@receiver(post_save, sender=Job)
def process_job(sender, instance, created, *args, **kwargs):
    "Starts job's document validation and audit runnig"

    # Only for created jobs
    if not created:
        return
