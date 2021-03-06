from django.test import TestCase

from audits.models import Doctype
from runner.document_validation import DocumentValidatorProvider


class DoctypeTest(TestCase):

    def test_doctypes_must_associate_with_installed_validators(self):
        choices = [p[0] for p in Doctype.validator_choices]
        plugins = [p for p in DocumentValidatorProvider.plugins.keys()]

        self.assertEqual(choices, plugins)
