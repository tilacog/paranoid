from django.core.urlresolvers import reverse
from django.test import TestCase

from jobs.factories import JobFactory


class JobViewTest(TestCase):
    def setUp(self):
        
        self.job = JobFactory(num_documents=3)

    def test_new_job_view_uses_right_template(self):
        response = self.client.get(reverse(
            'new_job', args=[self.job.pk]
        ))
        self.assertTemplateUsed(response, 'new_job.html')

    def test_new_job_view_passes_job_to_response_context(self):
        response = self.client.get( reverse(
            'new_job', args=[self.job.pk]
        ))
        self.assertEqual(self.job, response.context['job'])
