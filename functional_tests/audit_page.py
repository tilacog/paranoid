from .page_objects import page_element
from .home_page import HomePage

class AuditPage(HomePage):

    audit_name = page_element(id="id_audit_name")
    audit_description = page_element(id="id_audit_description")

    def check(self):
        self.test.asserIn(self.audit_name.text, self.title)
        self.test.assertTrue(self.audit_name)
        self.test.assertTrue(self.audit_description)
