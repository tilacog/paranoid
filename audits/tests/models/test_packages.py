from django.test import TestCase
from django.core.exceptions import ValidationError

from audits.models import Package

class PackageTestCase(TestCase):

    def test_can_be_created_with_name_and_description(self):
        pkg = Package(name="IRPJ", description="test")
        pkg.full_clean()  # should not raise

    def test_cannot_be_created_blank(self):
        pkg = Package()
        with self.assertRaises(ValidationError):
            pkg.full_clean()
