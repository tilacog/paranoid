from django.test import TestCase

class JobViewTest(TestCase):
    def test_job_reived_view_uses_right_template(self):
        response = self.client.get('/jobs/1/')
        self.assertTemplateUsed(response, 'job_received.html')
