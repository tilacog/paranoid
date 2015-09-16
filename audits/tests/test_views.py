from unittest import skip
from django.core.urlresolvers import reverse
from django.test import TestCase

from audits.models import Package, Audit

class HomePageTest(TestCase):

    def test_redirects_aonymous_user_to_login_page(self):
        response = self.client.get(reverse('home_page'))
        login_url = reverse('login_page')

        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

    @skip('future tests')
    def test_renders_available_packages(self):
        pass

    @skip('future tests')
    def test_renders_available_audits(self):
        pass

    @skip('future tests')
    def test_do_not_render_unavailable_packages(self):
        pass

    @skip('future tests')
    def test_do_not_render_unavailable_packages(self):
        pass

class AuditPageTest(TestCase):

    def setUp(self):
        self.package = Package.objects.create(
            name='test pkg name',
            description='test pkg desc'
        )

        self.audit = Audit.objects.create(
            name="Papel de trabalho da ECF",
            description="bla bla bla",
            package=self.package,
            execution_script ='/path/to/somewhere/script.py',

        )

        self.response = self.client.get(reverse(
            'audit_page', args=[self.audit.id]
        ))

    def test_view_renders_audit_template(self):
        self.assertTemplateUsed(self.response, 'audit.html')


    def test_view_passes_the_right_object_to_template_context(self):
        self.assertEqual(self.audit, self.response.context['audit'])



    def test_response_contains_audit_name_and_description(self):
        self.assertContains(self.response, self.audit.name)
        self.assertContains(self.response, self.audit.description)

    @skip('future tests')
    def test_inexistent_audit_raises_404_error_and_renders_error_page(self):
        pass

    @skip('future tests')
    def test_only_logged_users_can_view(self):
        pass

    @skip('future tests')
    def test_user_cannot_view_audit_page_if_not_authorized(self):
        pass
