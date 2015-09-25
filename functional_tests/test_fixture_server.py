from audits.factories import AuditFactory, DoctypeFactory

from .base import FunctionalTest


class SendingFixturesToServer(FunctionalTest):

    def test_returning_user(self):

        audit = AuditFactory(
            name='SOME INTERESTING AUDIT',
            num_doctypes=3,
        )

        self.send_fixtures('audits')

        self.create_pre_authenticated_session('test@user.com', '123')
        self.browser.get(self.server_url)
        self.browser.find_element_by_link_text(audit.name).click()

        audit_name = self.browser.find_element_by_id("id_audit_name").text
        self.assertEqual(audit_name, audit.name)
