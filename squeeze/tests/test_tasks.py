import datetime
from unittest import TestCase, skip
from unittest.mock import Mock, patch

from jobs.models import Job
from squeeze.tasks import (MAIL_MESSAGES, build_messages, notify_admins,
                           notify_beta_users)


class BetaUserSuccessfulNotificationTestCase(TestCase):
    """Unit tests for the notifier function.
    """
    def setUp(self):
        email_patcher = patch('squeeze.tasks.send_mail')
        self.addCleanup(email_patcher.stop)
        self.patched_mailer = email_patcher.start()

        squeezejob_patcher = patch('squeeze.tasks.SqueezeJob')
        self.addCleanup(squeezejob_patcher.stop)
        self.patched_squeezejob_cls = squeezejob_patcher.start()

        message_builder_patcher = patch('squeeze.tasks.build_messages')
        self.addCleanup(message_builder_patcher.stop)
        self.patched_message_builder = message_builder_patcher.start()
        self.patched_message_builder.return_value = ('text', 'html')

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

    def test_sent_mail_to_real_user_email(self):
        """The mail must be sent to the real user email.
        """
        # Get call arguments for the mailer function.
        args, kwargs = self.patched_mailer.call_args

        self.assertIn(
            self.mock_squeezejob.real_user_email,
            kwargs['recipient_list'],
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
            {'squeezejob':self.mock_squeezejob}
        )

    def test_uses_messages_from_message_builder(self):
        args, kwargs = self.patched_mailer.call_args

        self.assertTupleEqual(
            (kwargs['message'], kwargs['html_message']),
            self.patched_message_builder.return_value
        )


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


class NotifyAdminsTestCase(TestCase):
    """Unit tests for the notify_admin task.
    """

    def setUp(self):
        email_patcher = patch('squeeze.tasks.send_mail')
        self.addCleanup(email_patcher.stop)
        self.patched_mailer = email_patcher.start()


    def test_sends_email_to_admins(self):
        mock_request = Mock()

        notify_admins()

        self.patched_mailer.assert_any_calls()
