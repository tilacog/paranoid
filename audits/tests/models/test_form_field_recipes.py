from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest import skip

from audits.models import FormFieldRecipe


class FormFieldRecipeTest(TestCase):

    def test_can_create_a_minimal_form_field_recipe(self):
        field_recipe = FormFieldRecipe()

        field_recipe.name = 'test field_recipe name'
        field_recipe.input_label = 'test field_recipe label'
        field_recipe.form_field_class = 'BooleanField'
        field_recipe.tag = 'some doctype name'

        field_recipe.full_clean()  # should not raise
        field_recipe.save()        # should not raise

    def test_form_field_class_must_exist(self):
        """
        The form_field_class attribute must be one of
        django.forms.fields.Field instances.
        """

        field_recipe = FormFieldRecipe()

        # Valid values
        field_recipe.name = 'test field_recipe name'
        field_recipe.input_label = 'test field_recipe label'

        invalid_value = 'not_a_django_field_class'
        field_recipe.form_field_class =invalid_value

        with self.assertRaises(ValidationError) as e:
            field_recipe.full_clean()

        # Check if error was raised by invalid choice
        error_msg = "Value '{}' is not a valid choice.".format(invalid_value)
        self.assertIn(error_msg, e.exception.messages)
