from django.test import TestCase
from accounts.forms import LoginForm

import unittest
from unittest.mock import patch, Mock

class LoginFormTest(TestCase):

    def test_form_renders_login_fields(self):
        "LoginForms must render email and password fields"
        form = LoginForm()
        form_html = form.as_p()

        self.assertIn('id="id_email"', form_html)
        self.assertIn('name="email"', form_html)
        self.assertIn('type="email"', form_html)
        self.assertIn('placeholder="Email"', form_html)

        self.assertIn('id="id_password"', form_html)
        self.assertIn('name="password"', form_html)
        self.assertIn('type="password"', form_html)
        self.assertIn('placeholder="Senha"', form_html)


@patch('accounts.forms.authenticate')
class LoginFormValidationUnitTest(unittest.TestCase):

    def test_can_detact_inactive_user(self, mock_authenticate):
        mock_user = Mock(is_active=False)
        mock_authenticate.return_value = mock_user

        form = LoginForm()
        self.assertFalse(form.is_valid())

