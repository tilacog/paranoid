from django.test import TestCase
from django.forms import ModelForm, widgets
from django.forms.formsets import formset_factory

from audits.forms import DocumentForm
from unittest.mock import MagicMock

from audits.factories import DoctypeFactory

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


    def test_form_can_validate(self):
        DoctypeFactory()  # needed to set the choices of the doctype field.
        mock_file = MagicMock()

        post_data = {'doctype': 1}
        post_files = {'file': mock_file}

        form = DocumentForm(post_data, post_files)
        self.assertTrue(form.is_valid())

class DocumentFormsetTest(TestCase):

    def test_formset_can_validate(self):
        "Just a spike test"
        DoctypeFactory()
        mock_file = MagicMock()

        post_data = {
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS':'',
            'form-0-doctype': 1,
            'form-1-doctype': 1,
        }

        file_data = {
            'form-0-file': mock_file,
            'form-1-file': mock_file,
        }

        DocumentFormSet = formset_factory(DocumentForm)
        formset = DocumentFormSet(post_data, file_data)

        self.assertTrue(formset.is_valid())

    def test_invalid_data_doesnt_create_new_objects(self):
        # assert no objs exists
        # initialize formset with invalid data
        # form.is_valid()
        # assert no objs exist still
        pass

    def test_formset_save_instantiate_new_objects(self):
        # assert no objs exist
        # formset.save
        # assert expected objs now exist
        pass
