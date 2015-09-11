from .base import FunctionalTest
from .login_page import LoginPage

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
        login_page = LoginPage(self).visit()

        # The app name is featured in the page, and also in the browser tab.
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Titan', header_text.capitalize())
        self.assertIn('Titan', login_page.title.capitalize())

        # He is requested to insert his email and password.
        login_page.login(email='jacob@django.com', password='letsroque')

        # He tries to log in, but misspells his own email, resulting in an error.
        self.wait_for(self.assertEqual(
            'Usuário ou senha incorretos.',
            login_page.login_error.text
        ))

        # After retyping, he manages to successfull log in.

        # He then sees the main page, with his name displayed on screen.

        # There is also a navigation menu, with options for browsing available
        # audits.

        # He clicks on "ECF" and is taken to a page for creating new jobs.

        # There he can see that the audit name is featured with a descriptive
        # paragraph right below it.

        # He also notices a form to upload a new document.

        # But he gets too scared, and logs out in despair.
