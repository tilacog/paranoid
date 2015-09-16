from django.test import TestCase
from unittest import skip

from audits.models import KeyValueStore


class KeyValueStoreTest(TestCase):

    def test_can_create_a_minimal_key_value_store(self):
        "Can create a KVS with only required fields"
        kvs = KeyValueStore()
        kvs.name = 'test kvs name'
        kvs.input_label = 'test kvs label'
        kvs.formField_class = 'forms.BooleanField'
        kvs.taggedModel = 'audits.Audit'

        kvs.full_clean()  # should not raise
        kvs.save()        # should not raise

    # Future tests
    @skip('not a priority right now')
    def test_formfield_class_must_exist(self):
        pass

    @skip('not a priority right now')
    def test_taggedmodel_field_must_be_document_or_audit(self):
        pass
