from django.test import TestCase

from django.http import HttpRequest, HttpResponse
from django.core.urlresolvers import reverse
from unittest.mock import patch

from accounts.views import login_view


class LoginPageTest(TestCase):
    
    def setUp(self):
        self.request = HttpRequest()


    def test_login_view_exists(self):
        response = login_view(self.request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)

    def test_login_page_can_be_accessed(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_login_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'login.html')
   
    @patch('accounts.views.LoginForm')
    def test_view_passes_post_data_to_form(self, mockLoginForm):
        self.request.method == 'POST'
        self.request.POST['email'] = 'john@lennon.com'
        self.request.POST['password'] = 'allyouneedislove'
        login_view(self.request)
        mockLoginForm.assert_called_once_with(data=self.request.POST)

    @patch('accounts.views.LoginForm')
    @patch('accounts.views.render')
    def test_can_patch_render(self, mock_render, mockLoginForm):
        response = login_view(self.request)
        self.assertEqual(response, mock_render.return_value)

        mock_form = mockLoginForm.return_value

        mock_render.assert_called_once_with(
            self.request,
            'login.html',
            {'form': mock_form}
        )
