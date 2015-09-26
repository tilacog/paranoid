from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.factories import UserFactory
from jobs.factories import JobFactory


class NewJobViewTest(TestCase):

    def setUp(self):
        self.job = JobFactory(num_documents=3)
        user = UserFactory(email='test@user.com', password='123')
        self.client.login(email=user.email, password='123')

    def test_new_job_view_uses_correct_template(self):
        response = self.client.get(reverse(
            'new_job', args=[self.job.pk]
        ))
        self.assertTemplateUsed(response, 'new_job.html')

    def test_new_job_view_passes_job_to_response_context(self):
        response = self.client.get( reverse(
            'new_job', args=[self.job.pk]
        ))
        self.assertEqual(self.job, response.context['job'])

    def test_redirects_aonymous_user_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse(
            'new_job', args=[self.job.pk]
        ))
        login_url = reverse('login_page')

        # Can't use assertRedirects because url is different
        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

class JobViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@user.com', password='123')
        self.job = JobFactory(num_documents=3, user=self.user)
        self.client.login(email=self.user.email, password='123')

    def test_job_view_uses_correct_template(self):
        response = self.client.get(reverse('job_list'))
        self.assertTemplateUsed(response, 'job_list.html')

    def test_redirects_aonymous_user_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('job_list'))
        login_url = reverse('login_page')

        # Can't use assertRedirects because url is different
        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

    def test_job_view_passes_all_user_jobs_to_the_context(self):
        response = self.client.get(reverse('job_list'))
        self.assertEqual(
            list(response.context['jobs']), # Force to list to compare
            list(self.user.job_set.all())   # queryset.
        )
