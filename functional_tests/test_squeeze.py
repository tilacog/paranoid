from base import FunctionalTest

from accounts.factories import UserFactory
from audits.factories import AuditFactory


class SqueezeTest(FunctionalTest):
    "BDD tests for the squeeze page"

    def setUp(self):
        super().setUp()
        # Create base user
        self.password = '123'
        self.admin_user = UserFactory(password=self.password)
        self.admin_user.save()

        # Create audit models
        AuditFactory(num_doctypes=1)

    def test_can_upload_a_sped_document_via_squeeze_page(self):
        """Users should be able to opt-in and schedule an audit.
        """
        # User visits the squeeze page URL

        # The page will have:
        # - an email form
        # - an audit select
        # - an upload button

        # The user will submit the form with an invalid email address

        # The site returns a warning about the invalid email

        # The user will then submit a valid form

        # After submitting the valid form, the user is taken to a confirmation
        # page.
        self.fail('Finish the test!')


    def test_can_visit_a_valid_download_link(self):
        """Valid links should point to a page with a download link.
        """
        pass

    def test_cant_visit_an_expired_download_link(self):
        """Expired links should point to a 'sorry' page.
        """
        pass
