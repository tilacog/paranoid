from unittest import TestCase
from unittest.mock import Mock, patch

from django.db.models import signals

from jobs.signals.handlers import process_job_signal


class SignalTest(TestCase):

    def test_signal_registry(self):
        """Job processing callback must be registered as a m2m_changed signal.
        """
        registered_functions = [r[1]() for r in signals.m2m_changed.receivers]
        self.assertIn(process_job_signal, registered_functions)

class ProcessJobSignalUnitTest(TestCase):
    """Unit tests for the `process_job_signal` function.
    """

    def setUp(self):
        task_patcher = patch('jobs.signals.handlers.process_job')
        self.addCleanup(task_patcher.stop)
        self.patched_task = task_patcher.start()

        self.call_args = [Mock(name='sender'),]
        self.call_kwargs = {
            'action':'post_add',
            'instance': Mock(name='instance'),
        }


    def test_dispatch_task(self):
        """`process_job_signal` should call `process_job.delay` with a job
        instance primary key as an argument.
        """
        process_job_signal(*self.call_args, **self.call_kwargs)

        self.patched_task.delay.assert_called_once_with(
            self.call_kwargs['instance'].pk
        )

    def test_doesnt_dispatch_task(self):
        """`process_job_signal` should not be called otherwise."""
        new_kwargs = dict(**self.call_kwargs)
        new_kwargs.update({'action': 'other'})

        process_job_signal(*self.call_args, **new_kwargs)

        self.assertFalse(self.patched_task.delay.called)
