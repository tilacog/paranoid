import os.path

import magic
from django.apps import apps
from django.conf import settings

from runner.plugin_mount import PluginMount


class ValidationError(Exception):
    "Base exception for validation-phase errors"
    pass

class DocumentTypeError(ValidationError):
    "To be raised when file has the wrong mime"
    pass

class DocumentFormatError(ValidationError):
    "To be raised when file format doesn't comply with validation rules"
    pass

class DocumentValidatorProvider(metaclass=PluginMount):
    """
    Mount point for plugins which refer to validations that can be performed.
    Plugins implementing this reference should provide the following attributes:

    Parameters
    ----------
    document_pk : the unique identifier of the document under validation.

    Methods
    -------

    validate : method to validate the file. Should return the file if ok, or
               raise a DocumentFormatError.

    """
    def __init__(self, document_pk):
        self.document_pk = document_pk
        self.error = None

    def _check_type(self):
        "Validates document file type using python-magic"
        # Getting model class dynamically to avoid circular imports
        Document = apps.get_model('audits', 'Document')
        document_instance = Document.objects.get(pk=self.document_pk)
        doc_file = os.path.join(
            settings.MEDIA_ROOT,
            document_instance.file.url,
        )
        mime = magic.from_file(doc_file, mime=True)
        if mime != document_instance.doctype.mime:
            raise DocumentTypeError('Wrong file type')

    def validate(self, file_obj):
        # This method should be defined in subclasses
        raise NotImplementedError

    def run(self):
        "Validates document file and stores errors if any"
        # Getting model class dynamically to avoid circular imports
        Document = apps.get_model('audits', 'Document')

        with Document.objects.get(pk=self.document_pk).file as document_file:
            try:
                self._check_type()
                self.validate(document_file)

            except ValidationError as exception:
                # Catches both DocumentTypeError or DocumentFormatError
                exception.args = (self.document_pk,)
                self.error = exception
