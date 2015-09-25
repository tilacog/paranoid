from django.test import TestCase

from audits.models import Doctype


class DoctypeTest(TestCase):

    def test_doctypes_can_be_created(self):
        doctype = Doctype(name='MANAD', parsing_instructions=None)
        doctype.full_clean()  # should not raise
