import datetime
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase as djangoTestCase
from django.utils import timezone

from jobs.models import Job
from squeeze.factories import SqueezejobFactory
from squeeze.models import SqueezeJob
from squeeze.tasks import (MAIL_MESSAGES, build_messages, notify_beta_users,
                           delete_expired_files)


class BetaUserSuccessfulNotificationTestCase(TestCase):
    """Unit tests for the notifier function.
    """
    def setUp(self):
        email_patcher = patch('squeeze.tasks.EmailMultiAlternatives')
        self.addCleanup(email_patcher.stop)
        self.patched_mailer = email_patcher.start()

        squeezejob_patcher = patch('squeeze.tasks.SqueezeJob')
        self.addCleanup(squeezejob_patcher.stop)
        self.patched_squeezejob_cls = squeezejob_patcher.start()

        message_builder_patcher = patch('squeeze.tasks.build_messages')
        self.addCleanup(message_builder_patcher.stop)
        self.patched_message_builder = message_builder_patcher.start()
        self.patched_message_builder.return_value = ('text', 'html')

        admin_patcher = patch('squeeze.tasks.ADMINS')
        self.addCleanup(admin_patcher.stop)
        self.patched_admins = admin_patcher.start()

        self.mock_squeezejob = Mock(
            job=Mock(state=Job.SUCCESS_STATE),
            notified_at='',
            random_key='secret',
            real_user_email='mock@user.com',
        )

        self.patched_squeezejob_cls.objects.filter.return_value = [
            self.mock_squeezejob,

        ]

        notify_beta_users()

    def test_queries_correct_squeezejobs(self):
        """Notifier function must query for unnotified jobs.
        """
        self.patched_squeezejob_cls.objects.filter.assert_called_with(
            notified_at__isnull=True,
        )

    def test_updates_squeezejobs_timestamp(self):
        """The notifier function must update all SqueezeJobs instance's
        timestamps.
        """
        self.assertIsInstance(
            self.mock_squeezejob.notified_at,
            datetime.datetime
        )
        self.mock_squeezejob.save.assert_called_once_with()

    def test_sent_mail_to_correct_recipients(self):
        """The mail must be sent to the real user email and to all admins.
        """
        # Get call arguments for the mailer function.
        args, kwargs = self.patched_mailer.call_args

        self.assertIn(
            self.mock_squeezejob.real_user_email,
            kwargs['to'],
        )

        self.assertEqual(
            self.patched_admins,
            kwargs['bcc']
        )

    def test_used_successful_msg_subject(self):
        """The mail must use the successful squeezejob template.
        """
        args, kwargs = self.patched_mailer.call_args

        self.assertEqual(
            kwargs['subject'],
            MAIL_MESSAGES['SUCCESS_SUBJECT'],
        )

    def test_calls_message_builder_with_correct_arguments(self):
        args, kwargs = self.patched_message_builder.call_args

        self.assertEqual(args, ('success',))

        self.assertEqual(
            kwargs['context'],
            {'squeezejob': self.mock_squeezejob}
        )

    def test_uses_messages_from_message_builder(self):
        _, expected_html_content = self.patched_message_builder.return_value
        mailer_instance = self.patched_mailer.return_value

        mailer_instance.attach_alternative.assert_called_once_with(
            expected_html_content, "text/html"
        )

    def test_message_sent(self):
        mailer_instance = self.patched_mailer.return_value
        mailer_instance.send.assert_called_once_with()


class MessageBuilderTestCase(TestCase):
    """Unit tests for the build_message function.
    """
    def setUp(self):
        render_to_string_patcher = patch('squeeze.tasks.render_to_string')
        self.addCleanup(render_to_string_patcher.stop)
        self.patched_render = render_to_string_patcher.start()

    def test_uses_correct_success_msg_templates(self):
        """Assert that render_to_string uses correct messages templates for
        successful calls.
        """
        build_messages(state='success', context=None)

        templates_used = {
            kwarg['template_name'] for kwarg in [
                call[1] for call in self.patched_render.call_args_list
            ]
        }

        expected_templates = {
            'success-email-body.txt',
            'success-email-body.html'
        }

        self.assertSetEqual(templates_used, expected_templates)

    def test_uses_correct_failure_msg_templates(self):
        """Assert that render_to_string uses correct messages templates for
        failed calls.
        """
        build_messages(state='failure', context=None)

        templates_used = {
            kwarg['template_name'] for kwarg in [
                call[1] for call in self.patched_render.call_args_list
            ]
        }

        expected_templates = {
            'failure-email-body.txt',
            'failure-email-body.html'
        }

        self.assertSetEqual(templates_used, expected_templates)

    def test_passes_context_forward(self):
        """Message builder must pass the given context to render_to_string.
        """
        # Call build_message twice
        mock_context = Mock()
        build_messages('success', mock_context)
        build_messages('failure', mock_context)

        contexts_used = {
            kwarg['context'] for kwarg in [
                call[1] for call in self.patched_render.call_args_list
            ]
        }

        # All the context objects are the same
        self.assertEqual(len(contexts_used), 1)
        self.assertIn(mock_context, contexts_used)


class RemoveExpiredDocumentsUnitTests(TestCase):
    """Unit tests for the delete_expired_files task.
    """

    @patch('squeeze.tasks.SqueezeJob')
    def test_calls_squeezejob_remove_files_method(self, squeezejob_cls):
        mock_sj = MagicMock()
        squeezejob_cls.objects.filter.return_value = [mock_sj]

        mock_doc = Mock()
        mock_sj.job.documents.all.return_value = [mock_doc]

        delete_expired_files()

        mock_sj.job.report_file.delete.assert_called_once_with()
        mock_doc.file.delete.assert_called_once_with()


class RemoveExpiredDocumentsIntegratedTests(djangoTestCase):
    """Integrated tests for the remove_expired_douments task.
    """
    def test_remove_files_from_correct_squeezejobs(self):
        """Upon expiry, squeezejobs must have some of their files deleted:
         - job.report_file
         - job.documents.all()
        """
        # Create a fresh squeezejob
        new_sj = SqueezejobFactory(job__has_report=True)
        # Take a snapshot of document list and report file for future asserts
        documents_snapshot = [doc.file for doc in new_sj.job.documents.all()]
        report_snapshot = new_sj.job.report_file

        # Create a squeezejob which just expired
        limit_sj = SqueezejobFactory(job__has_report=True)
        limit_sj.created_at = timezone.now() - SqueezeJob.DEFAULT_TIMEOUT
        limit_sj.save()

        # Create a really old squeezejob
        old_sj = SqueezejobFactory(job__has_report=True)
        old_sj.created_at = timezone.now() - timezone.timedelta(days=900)
        old_sj.save()

        # Call the tested funciton
        delete_expired_files()

        # Refresh current session objects from db
        for sj in (new_sj, limit_sj, old_sj):
            sj.job.refresh_from_db()

        # Check if expired documents are gone
        self.assertFalse(any(doc.file for doc in limit_sj.job.documents.all()))
        self.assertFalse(any(doc.file for doc in old_sj.job.documents.all()))

        # Check if report files are gone too
        assert_msg = "Report file should be deleted, but still exists."
        self.assertFalse(bool(limit_sj.job.report_file), assert_msg)
        self.assertFalse(bool(old_sj.job.report_file), assert_msg)

        # Check if fresh  documents are still there
        self.assertListEqual(
            [doc.file for doc in new_sj.job.documents.all()],
            documents_snapshot
        )

        # Check if fresh repoorts are still there too
        self.assertEqual(new_sj.job.report_file, report_snapshot)
