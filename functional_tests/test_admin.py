from selenium.webdriver.support.select import Select

from accounts.factories import UserFactory
from audits.factories import PackageFactory, DoctypeFactory

from .base import FunctionalTest

class AdminTest(FunctionalTest):

    def setUp(self):
        super().setUp()

        # Create a superuser
        self.password = '123'
        self.admin_user = UserFactory(password=self.password)
        self.admin_user.is_admin = True
        self.admin_user.save()

        # Create packages and doctypes for the new audit
        PackageFactory(name='TestPackage')
        DoctypeFactory(name='TestDoctype')

    def test_can_create_new_audit_via_admin_site(self):
        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.server_url + '/admin/')

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # She inserts her email and password
        email_input = self.browser.find_element_by_id('id_username')
        email_input.send_keys(self.admin_user.email)

        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(self.password + '\n')

        # Aftwer beign logged in, she visits the audit creation page
        audit_section = self.browser.find_element_by_css_selector('.model-audit')
        audit_section.find_element_by_css_selector('.addlink').click()

        # She inserts all the required information in order to create a new audit
        self.browser.find_element_by_id('id_name').send_keys('A new test audit')
        self.browser.find_element_by_id('id_description').send_keys('A text description for our new audit')

        package_dropdown = Select(self.browser.find_element_by_id('id_package'))
        package_dropdown.select_by_visible_text('TestPackage')

        doctype_selection = Select(self.browser.find_element_by_id('id_required_doctypes'))
        doctype_selection.select_by_visible_text('TestDoctype')

        runner_dropdown = Select(self.browser.find_element_by_id('id_runner'))
        runner_dropdown.select_by_visible_text('DummyAudit')

        # She then saves her new audit by clicking on the Save button
        self.browser.find_element_by_css_selector('.default').click()

        # A list page is displayed, and she can see her newly created audit is in there
        self.assertTrue(self.browser.find_element_by_link_text('A new test audit'))

        # Finally, she visits to the home page to check if her new audit is displayed
        self.browser.find_element_by_link_text('View site').click()
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('A new test audit', page_text)
