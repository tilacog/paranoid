import os.path

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


class Doctype(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)

    # Upgrade to FilePathFiled in the future
    parsing_instructions = models.CharField(
        max_length=4096, blank=True, null=False
    )


def document_filename(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/<user.email>/<filename>
    return '/'.join(['uploads', instance.user.email, filename])


class Document(models.Model):
    doctype = models.ForeignKey('Doctype')
    file = models.FileField(upload_to=document_filename)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    checksum = models.CharField(max_length=40, blank=True)

    def basename(self):
        return os.path.basename(self.file.name)
