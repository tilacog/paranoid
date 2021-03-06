import re
from unittest import skip
from unittest.mock import MagicMock, patch

from django.core.files import File
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse
from django.forms import BaseFormSet
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from accounts.factories import UserFactory
from audits.factories import AuditFactory, DoctypeFactory, DocumentFactory
from audits.forms import DocumentForm
from audits.models import Document
from audits.views import audit_page
from jobs.models import Job


class AuditPageGETTest(TestCase):
    """
    Tests for GET requests on audit_page view.
    """

    def setUp(self):
        # Setup Audit instance with some doctypes
        self.audit = AuditFactory(num_doctypes=3)

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

    @patch('audits.views.DocumentFormSet', autospec=True)
    def test_view_sends_formset_to_response_context(self, mock_formset_cls):
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
            doctype.pk for doctype in self.audit.required_doctypes.all()
        }

        self.assertSetEqual(formset_doctype_ids, expected_doctype_ids)

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
        self.audit = AuditFactory(num_doctypes=1)
        self.user = UserFactory(password='123')
        self.client.login(email=self.user.email, password='123')
        doctype = DoctypeFactory()

        self.post_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': '',
            'form-0-doctype': doctype.pk,
        }
        self.post_files = {
            'form-0-file': MagicMock(spec=File)
        }


    @patch('audits.views.DocumentFormSet', autospec=True)
    def test_formset_is_initialized_with_POST_data_and_files(
        self, mock_formset_cls
    ):

        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        request.POST = self.post_data
        request.FILES = self.post_files

        response = audit_page(request, self.audit.pk)

        mock_formset_cls.assert_called_once_with(self.post_data, self.post_files)

    def test_redirects_after_POST(self):
        # send post with valid data
        data = self.post_data.copy()
        data.update(self.post_files)

        response = self.client.post(
            reverse('audit_page', args=[self.audit.pk]),
            data
        )

        # Magic Number 1 is a replacement for ``job.pk``
        self.assertRedirects(response, reverse('new_job', args=[1]))

    @patch('audits.views.DocumentFormSet')
    def test_invalid_POST_data_renders_the_same_page(self, mock_formset_cls):
        # Mock the formset object with invalid data
        mock_formset = MagicMock(name='MockFormSet')
        mock_formset.is_valid.return_value = False

        # Patch the formset_factory and formset class
        mock_formset_cls.return_value = mock_formset

        # assert invalid data renders the same page,
        # with the same invalid formset.
        data = self.post_data.copy()
        data.update(self.post_files)

        response = self.client.post(
            reverse('audit_page', args=[self.audit.pk]),
            data
        )

        self.assertTemplateUsed(response, 'audit.html')

    def test_view_can_save_a_POST_request(self):
        # Assert no objecs exist prior to the test
        self.assertEqual(Document.objects.count(), 0)

        # Send a POST request
        data = self.post_data.copy()
        data.update(self.post_files)
        self.client.post(
            reverse('audit_page', args=[self.audit.pk]),
            data
        )

        # Assert new expected objects were created
        expected_num_documents = len(self.post_files)
        self.assertEqual(Document.objects.count(), expected_num_documents)
        self.assertEqual(Job.objects.count(), 1)

    def test_invalid_POST_data_doesnt_create_new_objects(self):
        # Assert no objecs exist prior to the test
        self.assertEqual(Document.objects.count(), 0)

        # Send a POST request without files
        self.client.post(
            reverse('audit_page', args=[self.audit.pk]),
            self.post_data
        )

        # Assert new expected objects were created
        self.assertEqual(Document.objects.count(), 0)


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
