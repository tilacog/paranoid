from django.core.urlresolvers import reverse

from accounts.factories import UserFactory
from audits.factories import AuditFactory

from .base import FunctionalTest

SQUEEZE_PAGE_VIEW_NAME = 'squeeze_page'


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
        self.browser.get(self.server_url + reverse(SQUEEZE_PAGE_VIEW_NAME))

        # The page will have:
        # a verbose title
        title = self.browser.find_element_by_name('h1')
        for keyword in ['titan', 'sped', 'análise', 'excel']:
            self.assertIn(keyword.lower(), title.text.lower())

        # an intro text
        intro_text = self.browser.find_element_by_id('id_intro_text')
        # an email form
        email_form = self.browser.find_element_by_id('id_email_form')
        # audit selection radio inputs
        audit_selection = self.browser.find_elements_by_css_selector(
            'input[type="radio"]'
        )

        # an upload button
        upload_button = self.browser.find_elements_by_css_selector(
            'button[type="submit"]'
        )

        # The user will submit the form with an invalid email address
        email_form.send_keys('blarhg@\n')

        # The site returns a warning about the invalid email
        self.wait_for_element_with_id('id_invalid_email_error')

        # The user will then submit a valid form
        email_form.send_keys('testtitan@mailinator.com\n')

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
