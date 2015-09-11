from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.utils.html import escape
from unittest import skip
from unittest.mock import patch
import unittest

from accounts.views import login_view
from accounts.forms import LoginForm, EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR


class LoginPageTest(TestCase):

    def setUp(self):
        self.url = reverse('login')
        self.response = self.client.get(self.url)

    def test_login_page_exists(self):
        self.assertEqual(self.response.status_code, 200)

    def test_login_page_uses_login_template(self):
        self.assertTemplateUsed(self.response, 'login.html')

    def test_displays_login_form(self):
        self.assertIsInstance(self.response.context['form'], LoginForm)
        self.assertContains(self.response, 'id="id_email"')
        self.assertContains(self.response, 'id="id_password"')

    @skip
    def test_invalid_input_shows_errors(self):
        response = self.client.post(self.url, data={
            'email':'', 'password':''
        })
        self.assertContains(response, escape(EMPTY_EMAIL_ERROR))
        self.assertContains(response, escape(EMPTY_PASSWORD_ERROR))



@patch('accounts.views.LoginForm')
class LoginFormUnitTests(unittest.TestCase):  # Not using django's TestCase

    def setUp(self):
        self.request = HttpRequest()
        self.response = login_view(self.request)

    def test_no_data_is_passed_to_form_on_get_request(self, mockLoginForm):
        self.request.method = 'POST'
        self.request.POST['email'] = 'john@leonnon.co.uk'

        login_view(self.request)

        mockLoginForm.assert_called_once_with(data=self.request.POST)

    def test_view_passes_post_data_to_form(self, mockLoginForm):
        self.request.method = 'POST'
        self.request.POST['email'] = 'john@leonnon.co.uk'

        login_view(self.request)

        mockLoginForm.assert_called_once_with(data=self.request.POST)

    @patch('accounts.views.render')
    def test_can_patch_render(self, mock_render, mockLoginForm):
        request = HttpRequest()
        response = login_view(request)
        self.assertEqual(response, mock_render.return_value)

        mock_form = mockLoginForm.return_value

        mock_render.assert_called_once_with(
            request,
            'login.html',
            {'form': mock_form}
        )
