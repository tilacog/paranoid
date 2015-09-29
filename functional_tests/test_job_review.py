import os
from tempfile import TemporaryDirectory

from selenium import webdriver

from jobs.factories import JobFactory
from jobs.models import Job

from .base import FunctionalTest
from .home_page import HomePage
from .job_pages import JobListPage


class JobReviewTest(FunctionalTest):

    def setUp(self):
        # Call parent class setUp method before customization
        super().setUp()
        # Dismiss the old browser for it can't be assigned with a new profile
        self.browser.close()

        # Create a temporary directory to receive downloads
        self.temp_dir = TemporaryDirectory(dir=os.getcwd())

        # Setup a firefox profile to auto-download files
        fp = webdriver.FirefoxProfile()

        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", self.temp_dir.name)
        fp.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "text/plain"
        )

        self.browser = webdriver.Firefox(firefox_profile=fp)

    def tearDown(self):
        # Remove the temporary directory and all its contents
        self.temp_dir.cleanup()

        # Call parent class tearDown method after customization
        super().tearDown()

    def test_user_can_review_her_jobs(self):
        # Fixtures
        job1 = JobFactory(user__email='test@user.com', user__password='123')
        job2 = JobFactory(
            user__email='test@user.com',
            user__password='123',
        )

        # Use .txt fixture to match profile auto-download options
        self.assign_report_file_to_job_instance(job2, ext='.txt')

        self.send_fixtures('accounts')
        self.send_fixtures('audits')
        self.send_fixtures('jobs')

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
            self.assertIn(
                job.created_at.astimezone().strftime("%d/%m/%Y %H:%M"),
                row.text
            )
            self.assertIn(job.get_state_display(), row.text)

        # She can see that a download link for her finished report is available
        self.assertTrue(job_list_page.download_links)

        # She clicks on it, and her file is downloaded
        job_list_page.download_links[0].click()

        # She notices a file apperared on her download directory...
        ## Check that the temp directory is not empty
        dir_contents = os.listdir(self.temp_dir.name)
        self.wait_for(lambda: self.assertGreater(
            len(dir_contents),
            0
        ))

        # ... and it isn't empty
        ## Check that the downloaded file is not empty
        downloaded_file = os.path.join(
            self.temp_dir.name,
            dir_contents[0]
        )
        
        ## Can't test this step on development, since django won't serve
        ## any media files.
        if not self.against_staging:
            return

        self.wait_for(lambda: self.assertGreater(
            os.path.getsize(downloaded_file),
            0
        ))
