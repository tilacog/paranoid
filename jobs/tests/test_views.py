from unittest.mock import Mock

from django.core.urlresolvers import reverse
from django.http import Http404, HttpRequest
from django.test import TestCase

from accounts.factories import UserFactory
from jobs.factories import JobFactory
from jobs.views import download_report


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

class JobListViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@user.com', password='123')
        self.job = JobFactory(num_documents=3, user=self.user)
        self.client.login(email=self.user.email, password='123')

    def test_job_list_view_uses_correct_template(self):
        response = self.client.get(reverse('job_list'))
        self.assertTemplateUsed(response, 'job_list.html')

    def test_redirects_aonymous_user_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('job_list'))
        login_url = reverse('login_page')

        # Can't use assertRedirects because url is different
        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)

    def test_job_list_view_passes_all_user_jobs_to_the_context(self):
        response = self.client.get(reverse('job_list'))
        self.assertEqual(
            list(response.context['jobs']), # Force to list to compare
            list(self.user.job_set.all())   # queryset.
        )

class ReportDownloadView(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@user.com', password='123')
        self.client.login(email=self.user.email, password='123')

        self.job = JobFactory(num_documents=3, user=self.user)
        self.job.report_file = Mock()
        self.job.report_file.name = 'mock_filename'

    def test_users_cant_download_other_users_report_files(self):
        """
        When a user requests for another user file, it should receive a 404
        error code.
        """
        other_user = UserFactory(email='other@user.com', password='123')
        self.client.login(email='other@user.com', password='123')

        request = HttpRequest()
        request.user = other_user

        with self.assertRaises(Http404):
            download_report(request, self.job.pk)

    def test_users_can_download_their_own_reports(self):
        response = self.client.get(reverse(
            'download_report', args=[self.job.pk]
        ))

        self.assertEqual(response.status_code, 200)

    def test_nginx_will_serve_report_files(self):
        response = self.client.get(reverse(
            'download_report', args=[self.job.pk]
        ))

        self.assertTrue(response.has_header('X-Accel-Redirect'))
