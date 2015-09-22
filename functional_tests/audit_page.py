from .home_page import HomePage
from .page_objects import multi_page_element, page_element


class AuditPage(HomePage):

    audit_name = page_element(id="id_audit_name")
    audit_description = page_element(id="id_audit_description")
    upload_forms = multi_page_element(css='.document-upload-form')
    file_inputs = multi_page_element(css='input[type="file"]')
    submit_button = page_element(id="id_submit_button")

    def check(self):
        self.test.assertTrue(self.audit_name)
        self.test.assertTrue(self.audit_description)
        self.test.assertTrue(self.upload_forms)
        self.test.assertTrue(self.file_inputs)
        self.test.assertIn(self.audit_name.text, self.title)
