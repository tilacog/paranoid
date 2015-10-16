from unittest import skip

from django.core.exceptions import ValidationError
from django.forms import Form
from django.test import TestCase

from audits.factories import AuditFactory, DoctypeFactory, PackageFactory
from audits.models import Audit, Doctype, Package

from runner.data_processing import AuditRunnerProvider


class AuditTestCase(TestCase):

    def test_audits_must_associate_with_installed_runners(self):
        choices = [p[0] for p in Audit.runner_choices]
        plugins = [p for p in AuditRunnerProvider.plugins.keys()]

        self.assertEqual(choices, plugins)
