from .base import FunctionalTest


class PollsTest(FunctionalTest):

    def test_can_create_new_audit_via_admin_site(self):
        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.server_url + '/admin/')

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # TODO: use the admin site to create an audit
        self.fail('finish this test')
