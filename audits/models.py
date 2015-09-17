from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from inspect import getmembers
from itertools import chain


class Package(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)


class Audit(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    package = models.ForeignKey('Package')
    # Upgrade 'execution_script' to FilePathFiled in the future
    execution_script = models.CharField(max_length=4096, blank=False, null=False)
    required_doctypes = models.ManyToManyField('Doctype')
    extra_fields = models.ManyToManyField('FormFieldRecipe')

    def clean(self):
        # Don't allow audits to be cleansed without at least one required doctype
        if not self.required_doctypes.all():
            raise ValidationError(
                {'required_doctypes': ("Audits must have at least one "
                                       "required doctype.")
                }
            )

    def build_form(self):
        """
        Create a Django form using data from Audit's instance.
        """
        form = forms.Form()

        # Doctype fields
        associations = {
            doctype.name: [
                field for field in self.extra_fields.all()
                if field.tag == doctype.name
            ]
            for doctype in self.required_doctypes.all()
        }

        # Audit fields (remainders)
        associations.update({
            'non_doctype_fields': [
                field for field in self.extra_fields.all()
                if field not in chain(*associations.values())
            ]
        })

        # Create form field object
        for i, item in enumerate(chain(*associations.values())):
            form.fields[i] = forms.fields.BooleanField()
        return form



class Doctype(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)

    # Upgrade to FilePathFiled in the future
    parsing_instructions = models.CharField(
        max_length=4096, blank=True, null=False
    )

class FormFieldRecipe(models.Model):
    """
    This object will loosely tag audits or doctypes, carrying information to
    dynamically build a form object, to be rendered on Audit pages.

    Its `tag` attribute is a loose reference to a `Doctype.name`, Otherwise,
    it will be a reference to the audit who invoked it.
    """

    def get_field_classes():
        """
        Scans and returns all django.forms.fields.Field subclasses.
        They will be used as choices for the `form_field_class` field.
        """
        for tup in getmembers(forms.fields):
            try:
                # The first element is a string, and the second is the
                # class itself.
                if (issubclass(tup[1], forms.fields.Field)
                    and tup[1] != forms.fields.Field
                ):
                    # Return values comply with Django's choice spec.
                    yield (tup[0], tup[0])
                else:
                    continue
            except TypeError:
                continue

    FIELD_CHOICES = tuple(get_field_classes())

    # Fields
    name = models.CharField(max_length=30)
    tag = models.CharField(max_length=30, blank=True)
    form_field_class = models.CharField(
        max_length=30, choices=FIELD_CHOICES,
    )
    input_label = models.CharField(max_length=30)
    tooltip_text = models.TextField(blank=True)

    def __str__(self):
        s = "{}".format(self.name)
        if self.tag:
            s += "({})".format(self.tag)
        return s

class Document(models.Model):
    doctype = models.ForeignKey('Doctype')
    file = models.FileField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    checksum = models.CharField(max_length=40, blank=True)
