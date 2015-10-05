import os.path

from django.conf import settings
from django.db import models

from runner.document_validation import DocumentValidatorProvider


class Package(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name


class Audit(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    package = models.ForeignKey('Package')
    # Upgrade 'execution_script' to FilePathFiled in the future
    execution_script = models.CharField(max_length=4096, blank=False, null=False)
    required_doctypes = models.ManyToManyField('Doctype')

    def __str__(self):
        return self.name

class Doctype(models.Model):

    validator_choices = lambda: (
        (p.__name__, p.__name__) for p in DocumentValidatorProvider.plugins
    )

    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    validator = models.CharField(
        max_length=120,
        choices=validator_choices(),
    )

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

    def __str__(self):
        return "{} Document".format(self.doctype)
