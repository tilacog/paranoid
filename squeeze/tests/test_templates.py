from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils.html import escape

from jobs.models import Job
from squeeze.factories import SqueezejobFactory


class SuccessfulEmailTest(TestCase):
    """Integrated tests for the successful email template.
    """

    def setUp(self):
        self.squeezejob = SqueezejobFactory()
        self.rendered_email = render_to_string(
            'success-email-body.html',
            {'squeezejob': self.squeezejob},
        )

    def test_variables_loaded_correctly(self):
        """Squeezejob instance variables must be correctly rendered on
        email template.
        """
        # Check for download link
        download_url = reverse(
            'download_squeezejob',
            args=[self.squeezejob.random_key],
        )
        download_url = 'http://' + settings.DOMAIN + download_url

        download_link = '<a href="%s"' % download_url
        self.assertIn(download_link, self.rendered_email)

        # Check for real user name
        self.assertIn(escape(self.squeezejob.real_user_name), self.rendered_email)

class SqueezejobExpiredTest(TestCase):
    """Integrated tests for the `expired.html` template.
    """

    def test_extends_base_template(self):
        response = self.client.get(reverse('expired_download_link'))
        self.assertTemplateUsed(response, 'generic-base.html')

    def test_contains_link_to_squeeze_page(self):
        response = self.client.get(reverse('expired_download_link'))
        self.assertContains(response, reverse('squeeze_page'))

class SqueezejobSuccesTest(TestCase):
    """Integrated tests for the succesfull optin template.
    """
    def setUp(self):
        self.squeezejob = SqueezejobFactory()

        self.response = self.client.get(reverse(
            'success_optin',
            args=[self.squeezejob.random_key],
        ))

    def test_renders_squeezejob_info(self):
        for info in [self.squeezejob.real_user_name,
                     self.squeezejob.real_user_email]:

              self.assertContains(self.response, info)

    def test_renders_job_state(self):
        """Response text should contain underlying job state.
        """
        choices = dict(Job.STATE_CHOICES)

        self.assertContains(
            self.response,
            choices[self.squeezejob.job.state],
        )

    def test_renders_download_link_if_available(self):
        self.squeezejob.job.state = Job.SUCCESS_STATE
        self.squeezejob.job.save()

        # Fetch page
        response = self.response = self.client.get(reverse(
            'success_optin',
            args=[self.squeezejob.random_key],
        ))

        # Assert link is displayed
        self.assertContains(response, self.squeezejob.download_link)

    def test_doesnt_render_download_link_if_unavailable(self):
        undownloadable_states = [Job.RECEIVED_STATE,
                                 Job.STARTED_STATE,
                                 Job.FAILURE_STATE]

        for state in undownloadable_states:
            # Change job state
            self.squeezejob.job.state = state
            self.squeezejob.job.save()

            # Fetch page
            response = self.response = self.client.get(reverse(
                'success_optin',
                args=[self.squeezejob.random_key],
            ))

            # Assert link isn't displayed
            self.assertNotContains(response, self.squeezejob.download_link)
