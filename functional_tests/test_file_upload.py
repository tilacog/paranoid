import os
import tempfile

from django.conf import settings

from accounts.factories import UserFactory
from audits.factories import AuditFactory

from .audit_page import AuditPage
from .base import FunctionalTest
from .home_page import HomePage
from .job_request_page import JobRequestPage


class FileUploadTest(FunctionalTest):

    def setUp(self):
        super().setUp()

        # Fixtures
        AuditFactory(
            name='Test Audit',
            num_doctypes=3,
        )

        self.send_fixtures('audit')

        self.create_pre_authenticated_session(
            email='test@user.com', password='123'
        )

        # Temp files
        self.tempfiles = [
            tempfile.NamedTemporaryFile()
            for i in range(3)
        ]
        for f in self.tempfiles:
            f.write(os.urandom(1024))
            f.seek(0)

    def tearDown(self):
        # Delete temp files
        for f in self.tempfiles:
            f.close()
            final_path = os.path.join(
                settings.MEDIA_ROOT,
                os.path.basename(f.name)
            )
            os.remove(final_path)

        super().tearDown()

    def test_returning_user_can_upload_a_file(self):

        # Open the browser and check that the user is logged in
        self.browser.get(self.server_url)
        home_page = HomePage(self)
        self.assertEqual(home_page.loged_user_email.text, 'test@user.com')

        # Visit the audit page, where uploads are made
        home_page.get_audit('Test Audit').click()
        audit_page = AuditPage(self)

        # Inject the file paths into the form and submit the form
        for form, f in zip(audit_page.file_inputs, self.tempfiles):
            form.send_keys(f.name)
        audit_page.submit_button.click()

        # Grab the filename text that the page displays after processing the upload
        job_request_page = JobRequestPage(self)
        uploaded_docs = {
            document.text
            for document in job_request_page.uploaded_documents
        }

        # Assert that the filename text matches the filename provided in the test
        file_names = { 
            os.path.basename(f.name)
            for f in self.tempfiles
        }
        
        self.assertSetEqual(file_names, uploaded_docs)

        # The user clicks on the return_home button and returns to the home_page
        job_request_page.return_home_button.click()
        home_page.check()
