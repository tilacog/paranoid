from .base import FunctionalTest
from jobs.factories import JobFactory
from jobs.models import Job
from .job_pages import JobListPage, JobDetailPage
from .home_page import HomePage


class JobReviewTest(FunctionalTest):

    def test_user_can_review_her_jobs(self):
        # Fixtures
        job1 = JobFactory(user__email='test@user.com', user__password='123')
        job2 = JobFactory(user__email='test@user.com', user__password='123')
        self.send_fixtures('jobs')
        self.send_fixtures('audits')

        self.create_pre_authenticated_session(
            email='test@user.com', password='123'
        )

        # An authenticated user visits his job overview page
        self.browser.get(self.server_url)
        home_page = HomePage(self)
        home_page.job_review_link.click()

        job_list_page = JobListPage(self)

        # She can see all her jobs are listed and detailed with the
        # job id, audit name and job status.
        check_pairs = [
            (row, job) for row in job_list_page.current_jobs
                       for job in Job.objects.all()
        ]
        for row, job in check_pairs:
            self.assertIn(str(job.pk), row.text)
            self.assertIn(job.audit.name, row.text)
            self.assertIn(job.creation_date, row.text)
            self.assertIn(job.status, row.text)

        # She clicks on the first row
        job_list_page.current_jobs[0].click()

        # A detail page for that job shows up
        job_detail_page = JobDetailPage(self)

        # She can see that a download link for her finished report is available
        self.assertTrue(job_detail_page.download_link)

        # She clicks on it, and her file is saved
        job_detail_page.download_link.click()
        self.fail('assert file exists somewhere')
