from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from squeeze.factories import SqueezejobFactory
from squeeze.models import SqueezeJob


class SqueezejobTestCase(TestCase):
    """Integrated tests for the SqueezeJob model.
    """

    def setUp(self):
        self.squeezejob = SqueezejobFactory()

    def test_can_resolve_its_own_download_link(self):
        expected_url = 'http://' + settings.DOMAIN + reverse(
            'download_squeezejob',
            args=[self.squeezejob.random_key],
        )

        self.assertEqual(
            expected_url,
            self.squeezejob.absolute_download_link,
        )
