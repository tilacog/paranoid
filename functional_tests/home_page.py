from .page_objects import page_element
from .paranoid_pages import ParanoidPage

class HomePage(ParanoidPage):

    def check(self):
        self.test.assertEqual(self.title, 'Titan')
