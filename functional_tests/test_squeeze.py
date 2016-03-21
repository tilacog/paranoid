import os

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

        # Create audit instance
        self.audit_value = 'EcfDump'
        AuditFactory(num_doctypes=1, runner=self.audit_value)

    def fill(self, field_id, value):
        """Helper method to fill values on form fields."""
        field = self.browser.find_element_by_id(field_id)
        field.send_keys(value)


    def test_can_upload_a_sped_document_via_squeeze_page(self):
        """Users should be able to opt-in and schedule an audit.
        """
        # User visits the squeeze page URL
        squeeze_page_url = self.server_url + reverse(SQUEEZE_PAGE_VIEW_NAME)
        self.browser.get(squeeze_page_url)

        # The page will have:
        # a verbose title
        title = self.browser.find_element_by_tag_name('h1')
        for keyword in ['sped', 'analise', 'excel']:
            self.assertIn(keyword.lower(), title.text.lower())

        # an intro text
        about_text = self.browser.find_element_by_id('id_about_text')
        self.assertIn('titan', about_text.text.lower())

        # an email form
        email_form = self.browser.find_element_by_id('id_optin_form')

        # audit selection radio inputs
        audit_selection = self.browser.find_elements_by_css_selector(
            'input[type="radio"]')

        submit_button = self.browser.find_element_by_css_selector(
            'input[type="submit"]')


        # The user fills and submits the form
        user_name, user_email = ('John Doe', 'test@user.com')
        self.fill('id_name', user_name)
        self.fill('id_email', user_email)
        self.browser.find_element_by_css_selector(
            'input[type="radio"][value="%s"]' % self.audit_value
        ).click()

        # Use this file as a dummy for upload
        self.fill('id_document', os.path.abspath(__file__))

        submit_button.click()

        # After submitting the valid form, the user is taken to a confirmation
        # page, which shows his name and email on a confirmation text.
        self.wait_for(lambda: self.assertIn('success', self.browser.current_url))
        confirmation_text = self.browser.find_element_by_id('id_confirmation_text')
        for keyword in [user_email, user_name]:
            self.assertIn(keyword.lower(), confirmation_text.text.lower())


    def test_can_visit_a_valid_download_link(self):
        """Valid links should point to a page with a download link.
        """
        pass

    def test_cant_visit_an_expired_download_link(self):
        """Expired links should point to a 'sorry' page.
        """
        pass
