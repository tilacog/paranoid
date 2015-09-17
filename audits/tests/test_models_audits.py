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


class AuditFormFactoryTest(TestCase):
    "Test case for the Audit model form factory method"

    def setUp(self):

        # Create specific related objects
        self.doctype1 = DoctypeFactory(name='manad')
        self.doctype2 = DoctypeFactory(name='fopag')
        self.doctypes = [self.doctype1,  self.doctype2]

        self.doctype1_fields = FormFieldRecipeFactory.create_batch(3, tag='manad')
        self.doctype2_fields = FormFieldRecipeFactory.create_batch(2, tag='fopag')
        self.audit_fields = FormFieldRecipeFactory.create_batch(2, tag='not_a_doctype')
        self.extra_fields = (
            self.doctype1_fields + self.doctype2_fields + self.audit_fields
        )

        # Create audit object using pre-defined related objects
        self.audit = AuditFactory(
            extra_fields=self.extra_fields,
            required_doctypes=self.doctypes
        )

    def test_audit_models_can_render_a_form(self):
        form = self.audit.build_form()
        self.assertIsInstance(form, Form)

    def test_rendered_form_has_required_fields(self):
        form = self.audit.build_form()
        self.assertEqual(len(form.fields), len(self.extra_fields))
        self.fail('finish test!') 
