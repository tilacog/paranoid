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

class LoginTest(FunctionalTest):


    def test_returning_user(self):

        ## Fixtures
        user_email = 'test@user.com'
        user_password = '123'


        audit = AuditFactory(
            name='ECF',
            num_doctypes=3
        )

        self.send_fixtures('audits')
        self.create_user(user_email, user_password)

        ## The test begins...
        # A user access the home page.
        self.browser.get(self.server_url)
        login_page = LoginPage(self)

        # The app name is featured in the page, and also in the browser tab.
        login_page.check()

        # He is requested to insert his email and password.
        login_page.login(email=user_email, password='wrong_password')

        # He tries to log in, but misspells his own email, resulting in an error.
        self.wait_for(lambda: self.assertEqual(
            'Usuário ou senha incorreto.',
            login_page.login_error_element.text
        ))

        # After retyping, he manages to successfull log in.
        login_page.email.clear()
        login_page.login(email=user_email, password=user_password)

        # He is taken to the home page.
        home_page = HomePage(self)
        self.wait_for(lambda : home_page.check())

        # There is a navigation bar with his email on it.
        self.assertEqual(home_page.loged_user_email.text, user_email)

        # He clicks on "ECF" and is taken to a page for creating new jobs.
        self.browser.find_element_by_link_text('ECF').click()

        # There he can see that the audit name is featured wipth a descriptive
        # paragraph right below it.
        audit_page = AuditPage(self)
        audit_page.check()
        self.assertEqual('ECF', audit_page.audit_name.text)
        self.assertTrue(audit_page.audit_description)

        # He also notices a form to upload a new document.
        self.assertTrue(audit_page.upload_forms)

        # But he gets too scared, and logs out in despair.
        audit_page.logout_link.click()
