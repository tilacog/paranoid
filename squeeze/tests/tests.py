from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from audits.factories import AuditFactory
from jobs.factories import JobFactory
from jobs.models import Job
from squeeze.forms import OptInForm
from squeeze.models import SqueezeJob


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

    def setUp(self):
        fake_audit = AuditFactory(
            num_doctypes=1,
            runner='EcfDump',
        )

        # Valid POST and file data
        self.valid_post_data = {
            'name':'José Teste',
            'email':'jose@teste.com.br',
            'audit': fake_audit.runner,
        }

        self.valid_file_data = {
            'document': SimpleUploadedFile("file.txt", b"file_content")
        }

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
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        self.assertTrue(form.is_valid())

    def test_form_save_instantiates_new_squeezejob(self):
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(SqueezeJob.objects.count(), 0)

        form.save()

        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(SqueezeJob.objects.count(), 1)

    def test_squeezejob_obj_has_same_info_as_optin_form(self):
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        squeezejob = form.save()

        self.assertEqual(form.data['name'], squeezejob.real_user_name)
        self.assertEqual(form.data['email'], squeezejob.real_user_email)
        self.assertEqual(form.data['audit'], squeezejob.job.audit.runner)

class ReceiveSqueezejobTest(TestCase):
    """Integrated tests for the `receive_squeezejob` view.
    """
    def setUp(self):
        # Fake data for a request
        fake_file = SimpleUploadedFile("file.txt", b"file_content")
        fake_audit = AuditFactory(
            num_doctypes=1,
            runner='EcfDump',
        )

        # A valid request
        self.response = self.client.post(
            reverse('receive_squeezejob'),
            data={
                'name': 'Test User',
                'audit': fake_audit.runner,
                'email': 'test@user.com',
                'document': fake_file,
            },
        )

    def test_redirects_to_success_page(self):
        squeezejob = SqueezeJob.objects.first()
        self.assertRedirects(
            self.response,
            reverse('success_optin', args=[squeezejob.random_key])
        )

    def test_squeezejob_instance_is_created(self):
        num_objects = SqueezeJob.objects.count()
        self.assertEqual(num_objects, 1)

    def test_accepts_only_post_requests(self):
        resp = self.client.get(reverse('receive_squeezejob'))
        self.assertEqual(resp.status_code, 405)
class SuccessPageTest(TestCase):
    """Integrated tests for the success/thank-you page.
    """
    def setUp(self):
        self.squeezejob = SqueezeJob.objects.create(
            job=JobFactory(num_documents=1),
            real_user_email='test@user.com',
        )

        self.response = self.client.get(reverse(
            'success_optin',
            args=[self.squeezejob.random_key],
        ))

    def test_success_page_exists_for_given_squeezejob(self):
        self.assertEqual(self.response.status_code, 200)

    def test_success_page_returns_404_for_unexistent_squeezejob(self):
        resp = self.client.get(reverse(
            'success_optin',
            args=['unexistent_squeezejob_key'],
        ))
        self.assertEqual(resp.status_code, 404)

    def test_view_renders_right_template(self):
        self.assertTemplateUsed(self.response, 'success.html')

    def test_view_context_has_correct_form(self):
        response_squeezejob = self.response.context['squeezejob']
        self.assertEqual(response_squeezejob, self.squeezejob)

    def test_renders_squeezejob_info(self):
        for info in [
            self.squeezejob.real_user_name,
            self.squeezejob.real_user_email,
            self.squeezejob.job.audit.name,
            self.squeezejob.job.documents.first().doctype.name,
        ]:
            self.assertContains(self.response, info)
