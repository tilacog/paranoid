from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ModelForm, widgets
from django.forms.formsets import BaseFormSet
from django.test import TestCase

from accounts.factories import UserFactory
from audits.factories import AuditFactory, DoctypeFactory
from audits.forms import DocumentForm, DocumentFormSet
from audits.models import Document


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
        d = DoctypeFactory()
        mock_file = MagicMock()

        post_data = {'doctype': d.pk}
        post_files = {'file': mock_file}

        form = DocumentForm(post_data, post_files)
        self.assertTrue(form.is_valid())

class DocumentFormsetTest(TestCase):

    def test_view_initializes_formset_with_audit_initial_data(self):
        """
        DocumentFormSet forms' fields must be labeled and initialized
        according to the audit object used in its initialization.
        """
        audit = AuditFactory(num_doctypes=3)  # fixture

        formset = DocumentFormSet(audit_pk=audit.pk)

        expected_labels = {dt.verbose_name for dt in audit.required_doctypes.all()}
        forms_labels = {form.fields['file'].label for form in formset}
        self.assertSetEqual(expected_labels, forms_labels)

        expected_doctype_pks = {dt.pk for dt in audit.required_doctypes.all()}
        forms_pks = {form.initial['doctype'] for form in formset}
        self.assertSetEqual(expected_doctype_pks, forms_pks)

    def create_formset_data(self):
        d = DoctypeFactory()
        test_file = SimpleUploadedFile('file_name', b'file_content')

        post_data = {
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS':'',
            'form-0-doctype': d.pk,
            'form-1-doctype': d.pk,
        }

        file_data = {
            'form-0-file': test_file,
            'form-1-file': test_file,
        }

        return (post_data, file_data)

    def test_formset_can_validate(self):
        "Just a spike test to learn about formset validation"

        post_data, file_data = self.create_formset_data()

        formset = DocumentFormSet(post_data, file_data)

        self.assertTrue(formset.is_valid())


    def test_formset_save_instantiate_new_objects(self):
        user = UserFactory()

        # assert no objs exist
        self.assertEqual(Document.objects.count(), 0)

        post_data, file_data = self.create_formset_data()
        formset = DocumentFormSet(post_data, file_data)
        formset.save(user)

        # assert expected objs now exist
        expected_num_documents = len(file_data)
        self.assertEqual(Document.objects.count(), expected_num_documents)


    def test_formset_save_return_new_documents_pks(self):
        user = UserFactory()

        post_data, file_data = self.create_formset_data()
        formset = DocumentFormSet(post_data, file_data)
        return_value = formset.save(user)

        expected_return_value = [i for i in range(1, len(file_data)+1)]

        self.assertEqual(return_value, expected_return_value)

    @patch('audits.forms.DocumentFormSet.is_valid', value=False)
    def test_formset_save_wont_create_new_objects_if_form_is_invalid(
        self, mock_form_method
    ):
        mock_form_method.return_value = False
        user = UserFactory()

        # assert no objs exist
        self.assertEqual(Document.objects.count(), 0)

        post_data, file_data = self.create_formset_data()
        formset = DocumentFormSet(post_data, file_data)

        with self.assertRaises(RuntimeError):
            formset.save(user.pk)

        self.assertEqual(Document.objects.count(), 0)
