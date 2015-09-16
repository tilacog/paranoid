from .page_objects import page_element
from .home_page import HomePage

class AuditPage(HomePage):

    audit_name = page_element(id="id_audit_name")
    audit_description = page_element(id="id_audit_description")

    def check(self):
        self.test.assertEqual(self.title, 'Titan - Nova Validação')
        self.test.assertTrue(self.audit_name)
        self.test.assertTrue(self.audit_description)
