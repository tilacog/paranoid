from django.core.urlresolvers import reverse
from django.test import TestCase


class SqueezePageTest(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('squeeze_page'))

    def test_can_get_squeeze_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_right_template(self):
        self.assertTemplateUsed(self.response, 'landing.html')

    def test_form_contains_basic_elements(self):
        self.assertContains(self.response, '<h1')
        self.assertContains(self.response, 'id="id_about_text"')
        self.assertContains(self.response, '<form')
        self.assertContains(self.response, 'id="id_email_form"')
        self.assertContains(self.response, 'id="id_name_field"')
        self.assertContains(self.response, 'id="id_email_field"')
        self.assertContains(self.response, 'type="email"')
        self.assertContains(self.response, 'type="radio"')
        self.assertContains(self.response, 'type="file"')
        self.assertContains(self.response, 'type="submit"')

class FormTest(TestCase):
            
    def test_email_field_is_required(self):
        pass

    def test_name_field_is_required(self):
        pass
    def test_file_upload_restrict_extensions(self):
        pass

