from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from audits.factories import AuditFactory
from jobs.factories import JobFactory
from squeeze.forms import OptInForm
from squeeze.models import SqueezeJob


class SqueezePageTest(TestCase):
    """Integrated tests for the landing page view.
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


class DownloadSqueezejobTest(TestCase):
    """Integrated tests for the download_squeezejob view.
    """
    def setUp(self):
        self.fail('Write this TestCase')
