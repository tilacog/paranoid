from django.test import TestCase
from unittest import skip

from audits.models import Audit, Package, Doctype

class AuditTestCase(TestCase):

    def setUp(self):
        self.package = Package.objects.create(
            name='test pkg name',
            description='test pkg desc'
        )


    def test_audits_can_be_instantiated(self):
        audit = Audit(
            name="Papel de trabalho da ECF",
            description="bla bla bla",
            package=self.package,
            execution_script ='/path/to/somewhere/script.py',

        )

        audit.save()
        audit.required_key_value_stores = None,
        # audit.required_doctypes = [self.doctype]

        audit.full_clean()  # shoud not raise


