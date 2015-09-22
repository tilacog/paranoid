from .base import FunctionalTest
from .login_page import LoginPage
from .home_page import HomePage
from .audit_page import AuditPage

from accounts.factories import UserFactory
from audits.factories import AuditFactory, DoctypeFactory


"""
Keep in mind that .base.FunctionalTest has those methods:

class FunctionalTest(StaticLiveServerTestCase):
    def create_pre_authenticated_session(self, email):
    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
    def wait_for_element_with_id(self, element_id):
"""

class FirstTest(FunctionalTest):


    def test_returning_user(self):

        ## Fixtures
        # Create audit obj
        audit = AuditFactory(
            name='ECF',
            required_doctypes=DoctypeFactory.create_batch(3)
        )
       
        # Create test user
        user = UserFactory(email='test@user.com')
        user.set_password('123')
        user.save()

        # Authenticate this user
        self.client.login(email=user.email, password='123')
        cookie = self.client.cookies['sessionid']
        self.browser.get(self.server_url + '/404-dont-exist/')
        self.browser.add_cookie(dict(
            name='sessionid',
            value=cookie.value,
            secure=False,
            path='/'
        ))
        self.browser.refresh()
        
        
        ## The test begins...
        # Open the browser and check that the user is logged in
        
        self.browser.get(self.server_url)
        home_page = HomePage(self)
        self.assertEqual(home_page.loged_user_email.text, 'test@user.com')

        # Visit the audit page, where uploads are made
        
        # Inject the file paths into the form and submit the form

        # Grab the filename text that the page displays after processing the upload

        # Assert that the filename text matches the filename provided in the test

