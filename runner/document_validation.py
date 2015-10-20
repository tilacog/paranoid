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

# TODO: Decouple from django. Use json only
class DocumentValidatorProvider(metaclass=PluginMount):
    """
    Mount point for plugins which refer to validations that can be performed.
    Plugins implementing this reference should provide the following attributes:

    Init Parameters
    ---------------
    document_pk : the unique identifier of the document under validation.

    Methods
    -------
    validate : method to validate the file. Should return the file if ok, or
               raise a DocumentFormatError.
               A reference to the file path can be found at `self.file_path`

    """
    def __init__(self, document_pk):
        self.error = None

        # Keep a reference to the file path
        # (Getting model class dynamically to avoid circular imports)
        Document = apps.get_model('audits', 'Document')
        document_instance = Document.objects.get(pk=document_pk)

        self.file_path = document_instance.file.path
        self.document_pk = document_pk
        self.expected_mime = document_instance.doctype.mime

    def _check_type(self):
        "Validates document file type using python-magic"
        mime = magic.from_file(self.file_path, mime=True)
        if mime != self.expected_mime:
            raise DocumentTypeError(self.document_pk)

    def validate(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def run(self):
        "Validates document file and stores errors if any"
        # Getting model class dynamically to avoid circular imports

        with open(self.file_path) as document_file:
            try:
                self._check_type()
                self.validate(document_file)

            except ValidationError as e:
                # Catch and return error name and document pk
                return {'error': e.__class__.__name__, 'pk':  self.document_pk}
            else:
                return {'error': None, 'pk':  self.document_pk}
