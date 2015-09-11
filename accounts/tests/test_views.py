from django.test import TestCase

from django.http import HttpRequest, HttpResponse
from django.core.urlresolvers import reverse
from unittest.mock import patch
from unittest import skip

from accounts.views import login_view
from accounts.forms import LoginForm


class LoginPageTest(TestCase):
    
    def setUp(self):
        url = reverse('login')
        self.response = self.client.get(url)

    def test_login_page_exists(self):
        self.assertEqual(self.response.status_code, 200)

    def test_login_page_uses_login_template(self):
        self.assertTemplateUsed(self.response, 'login.html')

    def test_displays_login_form(self):
        self.assertIsInstance(self.response.context['form'], LoginForm)
        self.assertContains(self.response, 'id="id_email"')
        self.assertContains(self.response, 'id="id_password"')

    @patch('accounts.views.LoginForm')
    def test_view_passes_post_data_to_form(self, mockLoginForm):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['email'] = 'john@leonnon.co.uk'

        login_view(request)
        
        mockLoginForm.assert_called_once_with(data=request.POST)

    @patch('accounts.views.LoginForm')
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
