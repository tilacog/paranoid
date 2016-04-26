from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils.html import escape

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
