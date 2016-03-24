from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from jobs.models import Job
from jobs.tasks import process_job


@receiver(m2m_changed, sender=Job.documents.through)
def process_job_signal(sender, **kwargs):
    "Starts job's document validation and audit runnig."

    # Act only if new documents were added to the job.
    if kwargs['action'] == 'post_add':
        instance = kwargs['instance']
        process_job.delay(instance.pk)
