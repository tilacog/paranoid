from django.test import TestCase
from audits.factories import PackageFactory, AuditFactory


class FactoryTestCase(TestCase):
    def test_create_package(self):
        pkg = PackageFactory.create()

    def test_create_audit(self):
        audit = AuditFactory.create()

