import os.path

from django.conf import settings
from django.db import models

from runner.data_processing import AuditRunnerProvider
from runner.document_validation import DocumentValidatorProvider


class Package(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name


class Audit(models.Model):

    runner_choices = [
        # Django choices come in pairs
        (plugin,)*2 for plugin in AuditRunnerProvider.plugins.keys()
    ]

    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    package = models.ForeignKey('Package')
    required_doctypes = models.ManyToManyField('Doctype')
    runner = models.CharField(max_length=120, choices=runner_choices)


    def get_runner(self):
        return AuditRunnerProvider.plugins[self.runner]

    def __str__(self):
        return self.name

class Doctype(models.Model):

    # Django choices come in pairs, so we need to duplicate each choice
    # value.
    validator_choices = [
        (plugin,)*2 for plugin in DocumentValidatorProvider.plugins.keys()
    ]

    encoding_choices = (
        ('', '-----'),  # option for binary files
        ('utf_8', 'utf-8'),
        ('iso8859-1', 'latin-1'),
        ('cp1252', 'windows_1252' ),
        ('cp850', 'cp850'),
    )

    name = models.CharField(max_length=30, primary_key=True)
    validator = models.CharField(max_length=120, choices=validator_choices)
    mime = models.CharField(max_length=60, default='text/plain')
    expected_encoding = models.CharField(
        blank=True,
        max_length=25,
        choices=encoding_choices,
        default='utf_8'
    )

    def get_validator(self):
        return DocumentValidatorProvider.plugins[self.validator]

    def __str__(self):
        return self.name

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

    def get_absolute_path(self):
        # the first `file` is the FileField, and the second is the `FieldFile`
        return self.file.file.name

    def __str__(self):
        return "{} Document".format(self.doctype)
