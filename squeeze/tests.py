from django.core.urlresolvers import reverse
from django.test import TestCase


class SqueezePageTest(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('squeeze_page'))

    def test_can_get_squeeze_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_right_template(self):
        self.assertTemplateUsed(self.response, 'landing.html')

    def test_response_contains_basic_elements(self):
        self.assertContains(self.response, '<h1>')
