# This file is required for working with signals

from django.apps import AppConfig

class JobConfig(AppConfig):
    name = 'jobs'

    def ready(self):
        import jobs.signals.handlers
