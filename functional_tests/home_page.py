from .page_objects import multi_page_element, page_element
from .paranoid_pages import ParanoidPage


class HomePage(ParanoidPage):

    loged_user_email = page_element(id="id_user_email")
    logout_link = page_element(link_text="Logout")

    def check(self):
        self.test.assertEqual(self.title, 'Titan')
        self.test.assertTrue(self.logout_link)

    def get_audit(self, link_text):
        return self.browser.find_element_by_link_text(link_text)
