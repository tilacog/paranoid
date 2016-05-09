from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from audits.factories import AuditFactory
from jobs.models import Job
from squeeze.forms import CHOICES, OptInForm
from squeeze.models import SqueezeJob


class OptInFormTest(TestCase):
    """Tests for the opt-in form.
    """

    def setUp(self):
        fake_audit = AuditFactory(num_doctypes=1)

        # Valid POST and file data
        self.valid_post_data = {
            'name': 'José Teste',
            'email': 'jose@teste.com.br',
            'audit': '1',  # magic number because the first model has pk==1
        }

        self.valid_file_data = {
            'document': SimpleUploadedFile("file.txt", b"file_content")
        }

    def test_all_required_fields(self):
        form = OptInForm({
            'name': '',
            'email': '',
            'audit': '',
            'document': '',
        })

        form.is_valid()

        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('audit', form.errors)
        self.assertIn('document', form.errors)

    def test_form_validation_for_valid_data(self):
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        self.assertTrue(form.is_valid())

    def test_form_save_instantiates_new_squeezejob(self):
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(SqueezeJob.objects.count(), 0)

        form.save()

        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(SqueezeJob.objects.count(), 1)

    def test_squeezejob_obj_has_same_info_as_optin_form(self):
        form = OptInForm(self.valid_post_data, self.valid_file_data)
        form.is_valid()
        squeezejob = form.save()

        self.assertEqual(form.cleaned_data['name'], squeezejob.real_user_name)
        self.assertEqual(form.cleaned_data['email'], squeezejob.real_user_email)
        self.assertEqual(int(form.cleaned_data['audit']), squeezejob.job.audit.pk)
