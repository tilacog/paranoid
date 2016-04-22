from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from audits.factories import DoctypeFactory


class DoctypeTestCase(TestCase):

    @patch('audits.models.DocumentValidatorProvider')
    def test_runner_field_validation(self, patched_provider):
        patched_provider.plugins = ['foo']

        # Bad doctype, should raise ValidationEror.
        with self.assertRaises(ValidationError):
            bad_doctype = DoctypeFactory(validator='bar')

        # Good doctype, should not raise.
        good_doctype = DoctypeFactory(validator='foo')
        good_doctype.clean()



    @patch('audits.models.Doctype.clean')
    def test_clean_is_called_on_save(self, patched_clean):
        doctype = DoctypeFactory()

        # Reset mock call count, because Factoryboy already called it before.
        patched_clean.reset_mock()

        doctype.save()
        patched_clean.assert_called_once_with()
