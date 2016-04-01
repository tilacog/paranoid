from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from squeeze.factories import SqueezejobFactory


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

    def test_can_resolve_expiry_dates(self):
        """Instances can infer if they're expired.
        """
        # Recently created instance isn't expired
        self.assertFalse(self.squeezejob.is_expired)

        # Create an expired instance
        expired_sj = SqueezejobFactory()
        expired_sj.created_at = now() - timedelta(days=360)

        self.assertTrue(expired_sj.is_expired)
