from django.test import TestCase
from django.forms import ModelForm, widgets
from django.forms.formsets import formset_factory

from audits.forms import DocumentForm


class DocumentFormTest(TestCase):

    def test_document_form_exists(self):
        form = DocumentForm()
        self.assertIsInstance(form, ModelForm)

    def test_document_form_has_right_fields(self):
        """
        Document form should have a file upload field and a hidden doctype-id field
        """
        form = DocumentForm()
        self.assertEqual(len(form.fields.keys()), 2)
        self.assertIn('file', form.fields.keys())
        self.assertIn('doctype', form.fields.keys())

    def test_document_doctype_field_is_hidden(self):
        form = DocumentForm()
        field = form.fields['doctype']
        widget = field.widget
        self.assertIsInstance(widget, widgets.HiddenInput)
