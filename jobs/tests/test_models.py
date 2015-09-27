from unittest.mock import MagicMock, patch

from django.core.files import File
from django.test import TestCase
from django.utils import timezone

from accounts.factories import UserFactory
from audits.factories import AuditFactory
from jobs.factories import JobFactory
from jobs.models import Job


class JobModelTest(TestCase):

    def setUp(self):
        self.job = Job()
        self.job.audit = AuditFactory()
        self.job.user = UserFactory()

    def test_jobs_can_be_created(self):
        self.job.full_clean()  # Should not raise
        self.job.save()        # Should not raise

    def test_job_initial_state(self):
        "Job initial state should be RECEIVED"
        self.assertEqual(self.job.state, Job.RECEIVED_STATE)

    def test_job_creation_timestamp(self):
        start = timezone.now()
        job = JobFactory()
        end = timezone.now()

        self.assertLessEqual(start, job.created_at)
        self.assertLessEqual(job.created_at, end)

    def test_job_report_url(self):
        "Fresh and unfinished jobs have no report file"
        job = JobFactory()
        with self.assertRaises(ValueError):
            job.report_file.url


    @patch('django.core.files.storage.default_storage._wrapped')
    def test_finished_job_report_url(self, storage_mock):
        file_mock = MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test_file.txt'

        storage_mock.url = MagicMock('url')
        storage_mock.url.return_value = file_mock.name
        storage_mock.save.return_value = file_mock

        self.job.add_report(file_mock)

        self.assertEqual(self.job.report_file, file_mock)
        self.assertEqual(self.job.state, Job.SUCCESS_STATE)
