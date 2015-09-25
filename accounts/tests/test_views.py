import unittest
from unittest import skip
from unittest.mock import Mock, patch

from django.contrib.auth import SESSION_KEY, get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.utils.html import escape

from accounts.forms import (EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR,
                            INACTIVE_USER_ERROR, INVALID_LOGIN_ERROR,
                            LoginForm)
from accounts.views import login_page

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

    def test_displays_empty_field_errors(self):
        response = self.client.post(self.url, data={
            'email':'', 'password':''
        })

        self.assertContains(response, escape(EMPTY_EMAIL_ERROR))
        self.assertContains(response, escape(EMPTY_PASSWORD_ERROR))

    def test_displays_invalid_input_error(self):
        response = self.client.post(self.url, data={
            'email':'nonexistent@user.com', 'password':'123'
        })
        self.assertContains(response, escape(INVALID_LOGIN_ERROR))

    def test_displays_inactive_user_error(self):
        # Must call create_user otherwise test will fail.
        user = User.objects.create_user(
            email='inactive@user.com', password='123'
        )
        user.is_active = False
        user.save()

        response = self.client.post(self.url, data={
            'email': 'inactive@user.com', 'password': '123'
        })

        self.assertContains(response, escape(INACTIVE_USER_ERROR))


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


    def test_redirects_on_successfull_login(self):
        user = User.objects.create_user(email='a@b.com', password='123')
        response = self.client.post(
            self.url,
            {'email':'a@b.com', 'password':'123'}
        )
        self.assertRedirects(response, reverse('home_page'))

    @patch('accounts.views.authenticate')
    def test_user_is_logged_in_session_on_success(self, mock_authenticate):
        user = User.objects.create_user(email='a@b.com', password='123')
        user.backend = ''  # required for auth_login to work
        mock_authenticate.return_value = user

        response = self.client.post(
            self.url,
            {'email':'a@b.com', 'password':'123'}
        )
        self.assertEqual(self.client.session[SESSION_KEY], user.pk)

    @patch('accounts.views.authenticate')
    def test_des_not_get_logged_in_on_failure(self, mock_authenticate):
        mock_authenticate.return_value = None
        self.client.post(self.url, {
            'email': 'a@b.com',
            'password': 'WRONG_PASSWORD'
        })
        self.assertNotIn(SESSION_KEY, self.client.session)
