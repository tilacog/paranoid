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


class AuditFormFactoryTest(TestCase):
    "Test case for the Audit model form factory method"

    def setUp(self):

        # Create specific related objects
        self.dt_name = 'manad'
        self.doctype_field = FormFieldRecipeFactory(tag=self.dt_name)
        self.audit_fields = FormFieldRecipeFactory.create_batch(2, tag=self.dt_name)
        self.doctype = DoctypeFactory(name=self.dt_name)

        # Create audit object using pre-defined related objects
        self.audit = AuditFactory(
            extra_audit_info=self.audit_fields,
            extra_doctype_info=[self.doctype_field],
        )

    def test_audit_models_have_the_build_form_method(self):
        form = self.audit.build_form()



