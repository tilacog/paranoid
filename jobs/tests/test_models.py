from django.utils import timezone
from django.test import TestCase

from accounts.factories import UserFactory
from audits.factories import AuditFactory
from jobs.factories import JobFactory
from jobs.models import Job


class NewJobModelTest(TestCase):

    def setUp(self):
        self.new_job = Job()
        self.new_job.audit = AuditFactory()
        self.new_job.user = UserFactory()

    def test_jobs_can_be_created(self):
        self.new_job.full_clean()  # Should not raise
        self.new_job.save()        # Should not raise

    def test_job_initial_state(self):
        "Job initial state should be RECEIVED"
        self.assertEqual(self.new_job.state, Job.RECEIVED_STATE)

    def test_job_creation_timestamp(self):
        start = timezone.now()
        job = JobFactory()
        end = timezone.now()

        self.assertLessEqual(start, job.created_at)
        self.assertLessEqual(job.created_at, end)

    def test_job_get_report_url(self):
        "Fresh and unfinished jobs have no report file"
        job = JobFactory()
        with self.assertRaises(ValueError):
            job.report_file.url
