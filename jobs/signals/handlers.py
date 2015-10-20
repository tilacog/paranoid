from django.db.models.signals import post_save
from django.dispatch import receiver

from jobs.models import Job
from jobs.tasks import process_job


@receiver(post_save, sender=Job)
def process_job_signal(sender, instance, created, *args, **kwargs):
    "Starts job's document validation and audit runnig"

    # Only for created jobs
    if not created:
        return
    # Lauch celery task
    process_job.delay(instance.pk)
