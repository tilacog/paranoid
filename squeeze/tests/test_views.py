from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from audits.factories import AuditFactory
from jobs.factories import JobFactory
from jobs.models import Job
from squeeze.factories import SqueezejobFactory
from squeeze.forms import OptInForm, get_beta_user
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

    def test_tracking_code_present(self):
        """Tracking code must be present in context and in the rendered
        template.
        """
        tracking_code = 'some-random-tracking-code-string'
        with self.settings(GOOGLE_ANALYTICS_PROPERTY_ID=tracking_code,
                           DEBUG=False):
            response = self.client.get(reverse('squeeze_page'))
            self.assertIn('GOOGLE_ANALYTICS_PROPERTY_ID', response.context)
            self.assertContains(response, tracking_code)

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
        self.squeezejob = SqueezejobFactory()

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
        for info in [self.squeezejob.real_user_name,
                     self.squeezejob.real_user_email,
                     self.squeezejob.job.audit.name,
                     self.squeezejob.job.documents.first().doctype.name]:

            self.assertContains(self.response, info)


class DownloadSqueezejobTest(TestCase):
    """Integrated tests for the download_squeezejob view.
    """
    def setUp(self):
        # Create a finished squeezejob.
        self.job = JobFactory(
            has_report=True,
            state=Job.SUCCESS_STATE,
            user=get_beta_user())
        squeezejob = SqueezejobFactory(job=self.job)

        self.response = self.client.get(reverse(
            'download_squeezejob', args=[squeezejob.random_key]
        ))

    def test_users_can_download_their_own_reports(self):
        self.assertEqual(self.response.status_code, 200)

    def test_nginx_will_serve_report_files(self):
        # This means that Nginx will serve the file
        self.assertTrue(self.response.has_header('X-Accel-Redirect'))

    def test_redirect_expired_download_links(self):
        """Expired download links should be redirected to a try-again page.
        """
        expired_squeezejob = SqueezejobFactory(job=self.job)
        expired_squeezejob.created_at = (
            timezone.now() - timezone.timedelta(days=360)
        )
        expired_squeezejob.save()
        assert expired_squeezejob.is_expired  # just checking

        response = self.client.get(reverse(
            'download_squeezejob', args=[expired_squeezejob.random_key]
        ))
        self.assertRedirects(response, reverse('expired_download_link'))

class ExpiredDownloadLinkPageTest(TestCase):
    """Integrated tests for the expired-download-link page.
    """
    def setUp(self):
        self.response = self.client.get(reverse('expired_download_link'))

    def test_page_exists(self):
        self.assertEqual(self.response.status_code, 200)

    def test_uses_correct_template(self):
        self.assertTemplateUsed(self.response, 'expired.html')
