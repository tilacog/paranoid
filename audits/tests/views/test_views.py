import re
from django.core.urlresolvers import reverse
from django.forms import BaseFormSet
from django.test import TestCase, RequestFactory
from unittest import skip
from unittest.mock import patch, Mock

from audits.models import Package, Audit
from audits.factories import AuditFactory, DoctypeFactory
from audits.views import audit_page
from audits.forms import DocumentForm

class HomePageTest(TestCase):

    def test_redirects_aonymous_user_to_login_page(self):
        response = self.client.get(reverse('home_page'))
        login_url = reverse('login_page')

        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

    @skip('future tests')
    def test_renders_available_packages_only(self):
        pass

class AuditPageTest(TestCase):

    def setUp(self):
        # Setup Audit instance with some doctypes
        self.audit = AuditFactory(
            required_doctypes=DoctypeFactory.create_batch(3)
        )

        # Some shortcuts
        self.url = reverse('audit_page', args=[self.audit.id])
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
    def test_view_passes_initial_data_to_formset(self, fake_formset_factory):
        # Set the formset instance to be a mock. It is the result of two calls:
        # one to the formset_factory and other to the formset class.
        mock_document_formset_cls = fake_formset_factory.return_value
        mock_formset = mock_document_formset_cls.return_value

        response = self.client.get(self.url)
        self.assertEqual(mock_formset, response.context['formset'])

    def test_response_context_contains_all_required_documents_forms(self):
        """
        Formsets should be rendered with pre-populated 'doctype' fields,
        according to the doctypes defined by the Audit instance.
        """
        formset = self.response.context['formset']

        ## First assert they're DocumentForms.
        for form in formset:
            self.assertIsInstance(form, DocumentForm)

        ## Then assert they're the Docforms for the required fields, defined
        ## on the Audit instance.

        # Those are the doctypes found inside the forms of the formset.
        formset_doctype_ids = { d['doctype'] for d in formset.initial }

        # And those are the doctypes defined by the Audit instance.
        expected_doctype_ids = {
            doctype.id for doctype in self.audit.required_doctypes.all()
        }

        self.assertEqual(formset_doctype_ids, expected_doctype_ids)

    def test_response_context_forms_labels_are_named_after_doctype_names(self):
        doctype_names = { d.name for d in self.audit.required_doctypes.all() }

        formset = self.response.context['formset']
        form_labels = { form.fields['file'].label for form in formset }

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
