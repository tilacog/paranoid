from django.forms import Form
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest import skip

from audits.models import Audit, Package, Doctype
from audits.factories import (
    PackageFactory, DoctypeFactory, AuditFactory, FormFieldRecipeFactory,
)


class AuditTestCase(TestCase):

    def setUp(self):
        self.package = PackageFactory()
        self.doctype = DoctypeFactory()


    def test_audits_can_be_instantiated(self):
        audit = Audit(
            name="Papel de trabalho da ECF",
            description="bla bla bla",
            package=self.package,
            execution_script ='/path/to/somewhere/script.py',
        )

        audit.save()

        audit.required_doctypes.add(self.doctype)
        audit.full_clean()
        audit.save()

    def test_audits_cannot_be_cleansed_without_required_doctypes(self):
        audit = Audit(
            name="Papel de trabalho da ECF",
            description="bla bla bla",
            package=self.package,
            execution_script ='/path/to/somewhere/script.py',
        )
        audit.save()
        with self.assertRaises(ValidationError):
            audit.full_clean()

    @skip('future tests')
    def test_execution_script_file_exists(self):
        pass
