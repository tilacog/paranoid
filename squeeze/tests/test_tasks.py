import datetime
from unittest import TestCase, skip
from unittest.mock import Mock, patch

from jobs.models import Job
from squeeze.tasks import MAIL_MESSAGES, notify_beta_users


class BetaUserNotificationTestCase(TestCase):
    """Unit tests for the notifier function.
    """
    def setUp(self):
        email_patcher = patch('squeeze.tasks.send_mail')
        self.addCleanup(email_patcher.stop)
        self.patched_mail_cls= email_patcher.start()

        squeezejob_patcher = patch('squeeze.tasks.SqueezeJob')
        self.addCleanup(squeezejob_patcher.stop)
        self.patched_squeezejob_cls= squeezejob_patcher.start()


    def test_notifier_queries_correct_squeezejobs(self):
        """Notifier function must query for unnotified jobs.
        """
        notify_beta_users()

        self.patched_squeezejob_cls.objects.filter.assert_called_with(
             notified_at='',
        )


    def test_notifier_updates_squeezejobs_timestamp(self):
        """The notifier function must update all SqueezeJobs
        instance's timestamps.
        """
        mock_squeezejob = Mock(notified_at='')
        self.patched_squeezejob_cls.objects.filter.return_value = [
            mock_squeezejob
        ]

        notify_beta_users()

        self.assertIsInstance(mock_squeezejob.notified_at, datetime.datetime)
        mock_squeezejob.save.assert_called_once_with()

    def test_notifier_sends_correct_msg_to_successful_squeezejobs(self):
        # Mock a successfull squeezejob instance.
        mock_job = Mock(state=Job.SUCCESS_STATE)
        mock_squeezejob = Mock(
            real_user_email='mock@user.com',
            job=mock_job
        )

        self.patched_squeezejob_cls.objects.filter.return_value = [
            mock_squeezejob,
        ]

        notify_beta_users()

        self.fail('Write this test!')
        # assertions:
        # 1.  sent to real user email
        # 2.  used successful msg subject
        # 3.  patch render_to_string:
        # 3.1 used success template
        # 3.2 download link is rendered inside context (catch at render_to_string arguments)
        # 5.  download link in rendered msg (result of mocked render_to_string used as msg argument)


    def test_notifier_sends_correct_msg_to_failed_squeezejobs(self):
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
