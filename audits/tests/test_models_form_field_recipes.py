from django.test import TestCase
from unittest import skip

from audits.models import FormFieldRecipe


class FormFieldRecipeTest(TestCase):

    def test_can_create_a_minimal_key_value_store(self):
        "Can create a KVS with only required fields"
        field_recipe = FormFieldRecipe()
        field_recipe.key = 'test field_recipe name'
        field_recipe.input_label = 'test field_recipe label'
        field_recipe.form_field_class = 'forms.BooleanField'
        field_recipe.tag = 'audits.Audit'

        field_recipe.full_clean()  # should not raise
        field_recipe.save()        # should not raise

    # Future tests
    @skip('not a priority right now')
    def test_formfield_class_must_exist(self):
        pass

