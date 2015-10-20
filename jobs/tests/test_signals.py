from django.test import TestCase


class PostCreateSignalTest(TestCase):

    def test_signal_registry(self):
        """
        Job processing callback must be registered as a post_save signal.
        """
        from jobs.signals.handlers import process_job_signal
        from django.db.models import signals

        registered_functions = [r[1]() for r in signals.post_save.receivers]
        self.assertIn(process_job_signal, registered_functions)
