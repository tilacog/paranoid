from selenium.common.exceptions import NoSuchElementException

from .page_objects import PageObject, page_element


class LoginPage(PageObject):

    email = page_element(id='id_email')
    password = page_element(id='id_password')
    

    def landmark(self):
        self.test.assertEqual(self.browser.title, 'Titan')

    def visit(self):
        self.browser.get(self.test.server_url)
        self.test.wait_for(self.landmark)
        return self

    def login(self, email, password):
        self.visit()
        self.email = email
        self.password = password + '\n' 

    @property
    def login_error(self):
        return self.browser.find_element_by_css_selector('.has-error')
        

