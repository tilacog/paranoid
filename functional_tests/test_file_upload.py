from accounts.factories import UserFactory
from audits.factories import AuditFactory, DoctypeFactory

from .audit_page import AuditPage
from .base import FunctionalTest
from .home_page import HomePage
from .login_page import LoginPage


"""
Keep in mind that .base.FunctionalTest has those methods:

class FunctionalTest(StaticLiveServerTestCase):
    def create_pre_authenticated_session(self, email):
    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
    def wait_for_element_with_id(self, element_id):
"""

class FileUploadTest(FunctionalTest):


    def test_returning_user_can_upload_a_file(self):

        ## Fixtures
        # Create audit obj
        audit = AuditFactory(
            name='Test Audit',
            required_doctypes=DoctypeFactory.create_batch(3)
        )

        self.send_fixtures('audit')

        self.create_pre_authenticated_session(
            email='test@user.com', password='123'
        )

        ## The test begins...
        # Open the browser and check that the user is logged in
        self.browser.get(self.server_url)
        home_page = HomePage(self)
        self.assertEqual(home_page.loged_user_email.text, 'test@user.com')

        # Visit the audit page, where uploads are made
        home_page.get_audit('Test Audit').click()
        audit_page = AuditPage(self)

        # Inject the file paths into the form and submit the form
        # Grab the filename text that the page displays after processing the upload

        # Assert that the filename text matches the filename provided in the test
