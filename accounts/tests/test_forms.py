from django.test import TestCase

from accounts.forms import LoginForm


class LoginFormTest(TestCase):

    def test_form_renders_login_fields(self):
        "LoginForms must render email and password fields"
        form = LoginForm()
        form_html = form.as_p()

        self.assertIn('id="id_email"', form_html)
        self.assertIn('name="email"', form_html)
        self.assertIn('type="email"', form_html)
        
        self.assertIn('id="id_password"', form_html)
        self.assertIn('name="password"', form_html)
        self.assertIn('type="password"', form_html)


