from django.core.urlresolvers import reverse
from django.test import TestCase


class SqueezePageTest(TestCase):

    def test_can_get_squeeze_page(self):
        response = self.client.get(reverse('squeeze_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_right_template(self):
        response = self.client.get(reverse('squeeze_page'))
        self.assertTemplateUsed(response, 'landing.html')
