from django.test import TestCase
from django.http import HttpRequest, HttpResponse
from django.core.urlresolvers import reverse

from accounts.views import login_view


class LoginPageTest(TestCase):

    def test_login_view_exists(self):
        request = HttpRequest()
        response = login_view(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)

    def test_login_page_can_be_accessed(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_login_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'login.html')
