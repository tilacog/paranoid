from .base import FunctionalTest
from .login_page import LoginPage
from .home_page import HomePage

"""
Keep in mind that .base.FunctionalTest has those methods:

class FunctionalTest(StaticLiveServerTestCase):
    def create_pre_authenticated_session(self, email):
    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
    def wait_for_element_with_id(self, element_id):
"""

class FirstTest(FunctionalTest):

    def test_returning_user(self):

        # Jacob access the home page.
        self.browser.get(self.server_url)
        login_page = LoginPage(self)

        # The app name is featured in the page, and also in the browser tab.
        login_page.check()
        
        # He is requested to insert his email and password.
        login_page.login(email='jacob@django.com', password='letsroque')

        # He tries to log in, but misspells his own email, resulting in an error.
        self.wait_for(lambda: self.assertEqual(
            'Usuário ou senha incorreto.',
            login_page.login_error_element.text
        ))

        # After retyping, he manages to successfull log in.
        login_page.login(email='jacob@django.com', password='letsrock')
        
        # He is taken to the home page.
        home_page = HomePage(self)
        home_page.check()

        # There is also a navigation menu, with options for browsing available
        # audits.
        self.assertIn('Auditorias', home_page.navigation_links)

        # He clicks on "ECF" and is taken to a page for creating new jobs.
        self.browser.find_element_by_link_text('ECF').click()

        # There he can see that the audit name is featured with a descriptive
        # paragraph right below it.
        audit_page = AuditDetailPage(self)
        self.assertEqual('ECF', audit_page.audit_title)
        self.assertTrue(audit_page.audit_description)
        
        # He also notices a form to upload a new document.
        self.assertTrue(audit_page.upload_forms) 

        # But he gets too scared, and logs out in despair.
        audit_page.log_out()
        self.fail("Finish the test!")
