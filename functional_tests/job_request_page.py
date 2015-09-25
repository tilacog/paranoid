from .home_page import HomePage
from .page_objects import multi_page_element, page_element


class JobRequestPage(HomePage):

    audit_name = page_element(id="id_audit_name")
    uploaded_documents = multi_page_element(css=".uploaded-document")
    return_home_button = page_element(id="id_return_home_btn")

    def check(self):
        self.test.assertIn('Documentos Recebidos', self.title)
        self.test.assertTrue(self.audit_name)
        self.test.assertTrue(self.uploaded_documents)
        self.test.assertTrue(self.return_home_button)
