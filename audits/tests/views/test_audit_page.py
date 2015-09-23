import re
from unittest import skip
from unittest.mock import MagicMock, patch

from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.forms import BaseFormSet
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from audits.factories import (AuditFactory, DoctypeFactory, DocumentFactory,
                              UserFactory)
from audits.forms import DocumentForm
from audits.models import Document
from audits.views import audit_page


class AuditPageGETTest(TestCase):
    """
    Tests for GET requests on audit_page view.
    """

    def setUp(self):
        # Setup Audit instance with some doctypes
        self.audit = AuditFactory(
            required_doctypes=DoctypeFactory.create_batch(3)
        )

        # Some shortcuts
        self.url = reverse('audit_page', args=[self.audit.pk])
        self.response = self.client.get(self.url)

        # RequestFactory doesn't use middlweare, thus, no request.context.
        self.factory = RequestFactory()

    def test_view_renders_audit_template(self):
        self.assertTemplateUsed(self.response, 'audit.html')

    def test_response_contains_audit_name_and_description(self):
        self.assertContains(self.response, self.audit.name)
        self.assertContains(self.response, self.audit.description)

    def test_view_passes_the_right_object_to_template_context(self):
        self.assertEqual(self.audit, self.response.context['audit'])

    def test_view_passes_a_formset_to_template_context(self):
        formset = self.response.context['formset']
        self.assertIsInstance(formset, BaseFormSet)

    @patch('audits.views.formset_factory')
    def test_view_initializes_formset_with_audit_initial_data(
        self, fake_formset_factory
    ):
        # formset_factory returns a subclass of BaseFormset.
        mock_formset_cls = fake_formset_factory.return_value

        expected_init_data = [
            {'doctype': obj.id}
            for obj in self.audit.required_doctypes.all()
        ]

        response = self.client.get(self.url)

        mock_formset_cls.assert_called_with(initial=expected_init_data)

    @patch('audits.views.formset_factory')
    def test_view_sends_formset_to_response_context(self, fake_formset_factory):
        mock_formset_cls = fake_formset_factory.return_value
        mock_formset = mock_formset_cls.return_value

        response = self.client.get(self.url)
        self.assertEqual(mock_formset, response.context['formset'])

    def test_response_context_contains_all_required_documents_forms(self):
        """
        Formsets should be rendered with pre-populated 'doctype' fields,
        according to the doctypes defined by the Audit instance.
        """
        formset = self.response.context['formset']

        # First assert they're DocumentForms.
        for form in formset:
            self.assertIsInstance(form, DocumentForm)

        # Then assert they're the Docforms for the required fields, defined
        # on the Audit instance.

        # Those are the doctypes found inside the forms of the formset.
        formset_doctype_ids = {d['doctype'] for d in formset.initial}

        # And those are the doctypes defined by the Audit instance.
        expected_doctype_ids = {
            doctype.id for doctype in self.audit.required_doctypes.all()
        }

        self.assertEqual(formset_doctype_ids, expected_doctype_ids)

    def test_response_context_forms_labels_are_named_after_doctype_names(self):
        doctype_names = {d.name for d in self.audit.required_doctypes.all()}

        formset = self.response.context['formset']
        form_labels = {form.fields['file'].label for form in formset}

        self.assertEqual(doctype_names, form_labels)

    def test_response_context_has_exactly_one_form_per_required_doctype(self):
        num_forms = self.response.context['formset'].total_form_count()
        expected_forms = self.audit.required_doctypes.count()

        self.assertEqual(num_forms, expected_forms)

    def test_response_html_has_exactly_one_form_per_required_doctype(self):
        expected_num_forms = self.audit.required_doctypes.count()

        regex = re.compile(r'id="id_form-\d+-file"')
        matches = re.findall(regex, self.response.content.decode())
        total_forms_found = len(matches)

        self.assertEqual(
            total_forms_found,
            expected_num_forms,
            msg=self.response.content.decode(),
        )

    @skip('future tests')
    def test_inexistent_audit_raises_404_error_and_renders_error_page(self):
        pass

    @skip('future tests')
    def test_unauthenticated_users_cant_view_audit_page(self):
        pass

    @skip('future tests')
    def test_user_cannot_view_audit_page_if_his_group_isnt_authorized(self):
        pass


class AuditPagePOSTTest(TestCase):

    def setUp(self):

        # Fixtures
        self.audit = AuditFactory(
            required_doctypes=[DoctypeFactory()]
        )

        self.post_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS':'',
            'form-0-doctype': 1,
        }
        self.post_files = {
            'form-0-file': MagicMock(spec=File)
        }

    def test_view_can_save_a_POST_request(self):
        # assert no objs exist
        # send post request
        # assert the new *expected* objs exist
        #   * documents
        #   * a job
        pass

    @patch('audits.views.formset_factory')
    def test_formset_is_initialized_with_POST_data_and_files(
        self, mock_formset_factory
    ):
        # mock the formset class
        mock_formset_cls = MagicMock(name='MockFormSet')
        mock_formset_factory.return_value = mock_formset_cls

        # grab resquest.POST and request.FILES data
        request = HttpRequest()
        request.method = 'POST'
        request.POST = self.post_data
        request.FILES = self.post_files

        audit_page(request, 1)

        mock_formset_cls.assert_called_once_with(request.POST, request.FILES)

    def test_redirects_after_POST(self):
        # send post with valid data
        post_data = self.post_data.copy()
        post_data.update(self.post_files)

        response = self.client.post(
            reverse('audit_page', args=[self.audit.pk]),
            post_data
        )

        self.assertRedirects(response, reverse('job_received', args=[1]))

    def test_invalid_POST_data_renders_the_same_page(self):
        # patch render and formset.is_valid
        # assert invalid data renders the same page,
        # with the same invalid formset.
        pass

    ## FORMSET TEST ###
    def test_invalid_POST_data_doesnt_create_new_objects(self):
        # patch formset.is_valid
        # assert don't create a new job and document if form is
        # invalid/incomplete
        pass


class FileUploadsIsolatedTests(TestCase):
    """
    Tests isolated from Django's file and storage system.
    """

    def setUp(self):

        # Patch django storage system
        storage_patcher = patch(
            'django.core.files.storage.default_storage._wrapped',
            spec=Storage,
            name='StorageMock',
        )
        self.addCleanup(storage_patcher.stop)
        self.storage_mock = storage_patcher.start()
        self.storage_mock.url = MagicMock(name='url')
        self.storage_mock.url.return_value = 'some_test_file.test'

        # Mock a django file
        self.file_mock = MagicMock(spec=File, name='FileMock')
        self.file_mock.name = 'some_test_file.test'

    def test_mocking_works(self):

        document = DocumentFactory()
        document.file = self.file_mock
        document.full_clean()
        document.save()
