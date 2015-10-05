from unittest import skip

from django.core.exceptions import ValidationError
from django.forms import Form
from django.test import TestCase

from audits.factories import AuditFactory, DoctypeFactory, PackageFactory
from audits.models import Audit, Doctype, Package


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

    @skip('future tests')
    def test_execution_script_file_exists(self):
        pass
