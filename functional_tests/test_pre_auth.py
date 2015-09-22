from .base import FunctionalTest
from .management.commands.create_session_cookie import create_session_cookie


class FirstTest(FunctionalTest):

    def create_pre_auth(self, email, password):
        if self.against_staging:
            session_cookie = "something else"
            raise NotImplementedError("Should get some code here")

        session_cookie = create_session_cookie(email, password)

        self.browser.get(self.server_url + '/404/dont-exist/')
        self.browser.add_cookie(session_cookie)
        self.browser.refresh()

    def test_returning_user(self):

        # Fixtures
        self.create_pre_auth(
            email='test@user.com', password='123'
        )

        import ipdb; ipdb.set_trace()

        # Open the browser and check that the user is logged in
        self.browser.get(self.server_url)
