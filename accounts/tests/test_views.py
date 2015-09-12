from django.contrib.auth import get_user_model, SESSION_KEY
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.utils.html import escape
from unittest import skip
import unittest
from unittest.mock import patch

from accounts.views import login_page
from accounts.forms import LoginForm, EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR

User = get_user_model()


class LoginPageTest(TestCase):

    def setUp(self):
        self.url = reverse('login_page')
        self.response = self.client.get(self.url)

    def test_login_page_exists(self):
        self.assertEqual(self.response.status_code, 200)

    def test_login_page_uses_login_template(self):
        self.assertTemplateUsed(self.response, 'login.html')

    def test_displays_login_form(self):
        self.assertIsInstance(self.response.context['form'], LoginForm)
        self.assertContains(self.response, 'id="id_email"')
        self.assertContains(self.response, 'id="id_password"')

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
        self.response = login_page(self.request)

    def test_no_data_is_passed_to_form_on_get_request(self, mockLoginForm):
        self.request.method = 'POST'
        self.request.POST['email'] = 'john@leonnon.co.uk'

        login_page(self.request)

        mockLoginForm.assert_called_once_with(data=self.request.POST)

    def test_view_passes_post_data_to_form(self, mockLoginForm):
        self.request.method = 'POST'
        self.request.POST['email'] = 'john@leonnon.co.uk'

        login_page(self.request)

        mockLoginForm.assert_called_once_with(data=self.request.POST)

    @patch('accounts.views.render')
    def test_can_patch_render(self, mock_render, mockLoginForm):
        request = HttpRequest()
        response = login_page(request)
        self.assertEqual(response, mock_render.return_value)

        mock_form = mockLoginForm.return_value

        mock_render.assert_called_once_with(
            request,
            'login.html',
            {'form': mock_form}
        )


class LoginViewTest(TestCase):

    def setUp(self):
        self.url = reverse('login_view')

    @patch('accounts.views.authenticate')
    @patch('accounts.views.login')  # w/o this test crashes
    def test_calls_authenticate_from_post(self, mock_login, mock_authenticate):
        self.client.post(self.url)  # doesn't need any POST data for this test
        mock_authenticate.assert_called()


    def test_returns_OK_when_user_found(self):
        user = User.objects.create_user(email='a@b.com', password='123')
        response = self.client.post(
            self.url,
            {'email':'a@b.com', 'password':'123'}
        )

        self.assertEqual(response.status_code, 200)

    @patch('accounts.views.authenticate')  # have no interest in authenticate
    def test_gets_logged_in_session_on_success(self, mock_authenticate):
        user = User.objects.create_user(email='a@b.com', password='123')
        user.backend = ''  # required for auth_login to work
        mock_authenticate.return_value = user

        response = self.client.post(
            self.url,
            {'email':'a@b.com', 'password':'123'}
        )
        self.assertEqual(self.client.session[SESSION_KEY], user.pk)

    def test_des_not_get_logged_in_on_failure(self):
        self.fail()
