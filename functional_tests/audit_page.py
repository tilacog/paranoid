from .page_objects import page_element, multi_page_element
from .home_page import HomePage

class AuditPage(HomePage):

    audit_name = page_element(id="id_audit_name")
    audit_description = page_element(id="id_audit_description")
    upload_forms = multi_page_element(css='.document-upload-form')

    def check(self):
        self.test.assertTrue(self.audit_name)
        self.test.assertTrue(self.audit_description)
        self.test.assertTrue(self.upload_forms)
        self.test.assertIn(self.audit_name.text, self.title)
