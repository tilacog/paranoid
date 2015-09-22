from .base import FunctionalTest


class FirstTest(FunctionalTest):


    def test_returning_user(self):

        # Fixtures
        from audits.factories import AuditFactory, DoctypeFactory

        audit = AuditFactory(name='SOME INTERESTING AUDIT',
            required_doctypes=DoctypeFactory.create_batch(3)
        )

        self.send_fixtures('audits')

        self.create_pre_authenticated_session('test@user.com', '123')
        self.browser.get(self.server_url + '/audits/1')

        audit_name = self.browser.find_element_by_id("id_audit_name").text
        self.assertEqual(audit_name, audit.name)