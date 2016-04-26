from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from audits.factories import AuditFactory


class AuditTestCase(TestCase):

    @patch('audits.models.AuditRunnerProvider')
    def test_runner_field_validation(self, patched_provider):
        patched_provider.plugins = ['foo']

        # Bad audit, should raise ValidationEror.
        with self.assertRaises(ValidationError):
            bad_audit = AuditFactory(runner='bar')

        # Good audit, should not raise.
        good_audit = AuditFactory(runner='foo')
        good_audit.clean()



    @patch('audits.models.Audit.clean')
    def test_clean_is_called_on_save(self, patched_clean):
        audit = AuditFactory()

        # Reset mock call count, because Factoryboy already called it before.
        patched_clean.reset_mock()

        audit.save()
        patched_clean.assert_called_once_with()
