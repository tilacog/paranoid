from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from squeeze.forms import OptInForm


class SqueezePageTest(TestCase):
    """Tests for the landing page view.
    """
    def setUp(self):
        self.response = self.client.get(reverse('squeeze_page'))

    def test_can_get_squeeze_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_right_template(self):
        self.assertTemplateUsed(self.response, 'landing.html')

    def test_view_context_has_correct_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, OptInForm)


class OptInFormTest(TestCase):
    """Tests for the opt-in form.
    """
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

    def test_all_required_fields(self):
        form = OptInForm({
            'name':'',
            'email':'',
            'audit':'',
            'document':'',
        })

        form.is_valid()

        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('audit', form.errors)
        self.assertIn('document', form.errors)

    def test_form_validation_for_valid_data(self):
        valid_post_data = {
            'name':'José Teste',
            'email':'jose@teste.com.br',
            'audit':'1',
        }
        valid_file_data = {
            'document': SimpleUploadedFile("file.txt", b"file_content")
        }

        form = OptInForm(valid_post_data, valid_file_data)
        self.assertTrue(form.is_valid())



class ReceiveSqueezejobTest(TestCase):
    """Tests for handling squeeze page jobs.
    """
    def setUp(self):
        f = SimpleUploadedFile("file.txt", b"file_content")

        # TODO: Finish this setup
        self.response = self.client.post(
            reverse('receive_squeezejob'),
            data={'file': f},
        )

    def test_can_receive_squeeze_job(self):
        self.fail('Write this test!')
        # Assert a squeezejob instance is created
