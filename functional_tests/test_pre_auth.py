from .base import FunctionalTest


class FirstTest(FunctionalTest):


    def test_returning_user(self):

        # Fixtures
        self.create_pre_authenticated_session(
            email='test@user.com', password='123'
        )

        import ipdb; ipdb.set_trace()

        # Open the browser and check that the user is logged in
        self.browser.get(self.server_url)
