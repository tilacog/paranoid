from .page_objects import page_element
from .paranoid_pages import ParanoidPage

class LoginPage(ParanoidPage):

    email = page_element(id='id_email')
    password = page_element(id='id_password')
    
    def check(self):
        self.test.assertIn('Titan - Login', self.title)
        
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.test.assertIn('Titan', header_text.capitalize())
        

    def login(self, email, password):
        self.email = email
        self.password = password + '\n'

    @property
    def login_error_element(self):
        return self.browser.find_element_by_css_selector('.has-error')


