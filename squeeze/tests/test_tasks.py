import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from django.core.urlresolvers import reverse

from jobs.models import Job
from squeeze.tasks import MAIL_MESSAGES, notify_beta_users


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
            notified_at='',
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

        self.assertEqual(
            kwargs['to'],
            [self.mock_squeezejob.real_user_email],
        )

    def test_used_successful_msg_subject(self):
        """The mail must use the
        """
        args, kwargs = self.patched_mailer.call_args

        self.assertEqual(
            kwargs['subject'],
            MAIL_MESSAGES['SUCCESS_SUBJECT'],
        )

    @patch('squeeze.tasks.render_to_string')
    def test_used_successful_msg_template(self, patched_render_to_string):
        """Assert that render_to_string uses correct template.
        """
        notify_beta_users()  # Call again to use patched objects
        args, kwargs = patched_render_to_string.call_args

        self.assertEqual(
            kwargs['template_name'],
            'success_email_body.html',
        )

    @patch('squeeze.tasks.render_to_string')
    def test_used_correct_context_object(self, patched_render_to_string):
        """Assert that the context used by render_to_string contains
        squeezejob instance.
        """
        notify_beta_users()  # Call again to use patched objects
        args, kwargs = patched_render_to_string.call_args

        context = kwargs['context']

        self.assertEqual(context['squeezejob'], self.mock_squeezejob)

    @patch('squeeze.tasks.render_to_string')
    def test_used_successful_msg_content(self, patched_render_to_string):
        """Assert that the result of reder_to_string is used as the email body.
        """
        notify_beta_users()  # Call again to use patched objects
        args, kwargs = self.patched_mailer.call_args

        self.assertEqual(
            kwargs['html_message'],
            patched_render_to_string.return_value,
        )


    def test_failed_squeezejobs_have_different_msg(self):
        self.fail('Write thist test!')

    def test_sends_correct_msg_to_failed_squeezejobs(self):
        # Mock an unsuccessful squeezejob intance.
        mock_squeezejob = Mock(
            real_user_email='mock@user.com',
            job=Mock(state=Job.FAILURE_STATE),
        )

        self.patched_squeezejob_cls.objects.filter.return_value = [
            mock_squeezejob,
        ]

        notify_beta_users()

        self.fail('Write this test!')
        # assertions:
        # 1.  sent to real user email
        # 2.  used failure msg subject
        # 3.  used failure template (patch render_to_string)
