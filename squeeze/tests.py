from unittest import skip

from django.core.urlresolvers import reverse
from django.test import TestCase

from squeeze.forms import OptInForm


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

class OptInFormTest(TestCase):


    @skip('Will write later')
    def test_email_field_is_required(self):
        pass

    @skip('Will write later')
    def test_name_field_is_required(self):
        pass

    @skip('Will write later')
    def test_file_upload_restrict_extensions(self):
        pass

    def test_form_renders_login_fields(self):
        "OptInForm must render email and password fields"
        form = OptInForm()
        form_html = form.as_p()

        # Name
        self.assertIn('id="id_name"', form_html)
        self.assertIn('name="name"', form_html)
        self.assertIn('type="text"', form_html)
        self.assertIn('placeholder="Seu nome"', form_html)

        # Email
        self.assertIn('id="id_email"', form_html)
        self.assertIn('name="email"', form_html)
        self.assertIn('type="email"', form_html)
        self.assertIn('placeholder="Email"', form_html)

        # Audit Selection
        self.assertIn('id="id_audit"', form_html)
        self.assertIn('name="audit"', form_html)
        self.assertIn('type="radio"', form_html)

        # File Upload
        self.assertIn('id="id_file"', form_html)
        self.assertIn('name="document"', form_html)
        self.assertIn('type="file"', form_html)
