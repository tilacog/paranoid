from unittest import skip
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from audits.factories import AuditFactory, DoctypeFactory


class HomePageTest(TestCase):

    def test_redirects_aonymous_user_to_login_page(self):
        response = self.client.get(reverse('home_page'))
        login_url = reverse('login_page')

        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

    @skip('future tests')
    def test_renders_available_packages_only(self):
        pass

    def test_home_page_renders_available_audits(self):
        User = get_user_model()
        User.objects.create_user(email='test@user.com', password='123')
        self.client.login(email='test@user.com', password='123')

        audit = AuditFactory(num_doctypes=3)

        response = self.client.get(reverse('home_page'))

        audit_link_text = '{}</a>'.format(audit.name)
        self.assertContains(response, audit_link_text)

    def test_home_page_response_contains_available_audits(self):
        User = get_user_model()
        User.objects.create_user(email='test@user.com', password='123')
        self.client.login(email='test@user.com', password='123')

        audit = AuditFactory(num_doctypes=3)

        response = self.client.get(reverse('home_page'))

        self.assertIn(audit, response.context['audits'])
