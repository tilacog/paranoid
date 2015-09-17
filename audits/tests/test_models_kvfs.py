from django.test import TestCase
from unittest import skip

from audits.models import KeyValueFormStore


class KeyValueFormStoreTest(TestCase):

    def test_can_create_a_minimal_key_value_store(self):
        "Can create a KVS with only required fields"
        kvs = KeyValueFormStore()
        kvs.key = 'test kvs name'
        kvs.input_label = 'test kvs label'
        kvs.form_field_class = 'forms.BooleanField'
        kvs.tag = 'audits.Audit'

        kvs.full_clean()  # should not raise
        kvs.save()        # should not raise

    # Future tests
    @skip('not a priority right now')
    def test_formfield_class_must_exist(self):
        pass

