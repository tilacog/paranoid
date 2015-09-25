from inspect import getmembers
from itertools import chain

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


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


class Document(models.Model):
    doctype = models.ForeignKey('Doctype')
    file = models.FileField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    checksum = models.CharField(max_length=40, blank=True)
