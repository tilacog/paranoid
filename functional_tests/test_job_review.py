from .base import FunctionalTest
from jobs.factories import JobFactory
from jobs.models import Job
from .job_pages import JobListPage, JobDetailPage
from .home_page import HomePage


class JobReviewTest(FunctionalTest):

    def test_user_can_review_her_jobs(self):
        # Fixtures
        job1 = JobFactory(user__email='test@user.com', user__password='123')
        job2 = JobFactory(
            user__email='test@user.com',
            user__password='123',
            state=Job.SUCCESS_STATE,
        )


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
        check_pairs = zip(job_list_page.current_jobs, Job.objects.all())
        for row, job in check_pairs:
            self.assertIn(str(job.pk), row.text)
            self.assertIn(job.audit.name, row.text)
            self.assertIn(job.created_at.astimezone().strftime("%d/%m/%Y %H:%M"), row.text)
            self.assertIn(job.get_state_display(), row.text)

        # She can see that a download link for her finished report is available
        self.assertTrue(job_list_page.download_links)

        # She clicks on it, and her file is saved

        self.fail('Finish the test! Check that the downloaded file is on user'
                  ' drive, and its sha1 equals the one on the server')
