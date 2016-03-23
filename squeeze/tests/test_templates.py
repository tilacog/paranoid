from unittest import TestCase

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from squeeze.factories import SqueezejobFactory


class SuccessfulEmailTest(TestCase):

    def setUp(self):
        self.squeezejob = SqueezejobFactory()
        self.rendered_email = render_to_string(
            'success_email_body.html',
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
        self.assertIn(self.squeezejob.real_user_name, self.rendered_email)

