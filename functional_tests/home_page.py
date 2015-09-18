from .page_objects import page_element, multi_page_element
from .paranoid_pages import ParanoidPage

class HomePage(ParanoidPage):

    loged_user_email = page_element(id="id_user_email")

    def check(self):
        self.test.assertEqual(self.title, 'Titan')
