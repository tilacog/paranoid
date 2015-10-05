import os.path

import magic
from django.conf import settings

from audits.models import Document
from runner.plugin_mount import PluginMount


class DocumentTypeError(Exception):
    pass

class ValidationError(Exception):
    pass

class DocumentValidatorProvider(metaclass=PluginMount):
    """
    Mount point for plugins which refer to validations that can be performed.
    Plugins implementing this reference should provide the following attributes:

    Attributes
    ----------
    doctype : the name of the doctype handled by the validator

    Methods
    -------

    validate : method to validate the file. Should return the file if ok, or
               raise an appropriate valdiation error.
    
    """
    def __init__(self, document_pk):
        self.document_pk = document_pk
        self.error = None
        self.cleaned = False

    def _check_type(self):
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
        # Expect exceptions to be raised for each `try` clause statement, 
        # respectively
        with Document.objects.get(pk=self.document_pk).file as document_file:
            try:
                self._check_type()
                self.validate(document_file)
            except (DocumentTypeError, ValidationError) as e:
                self.error = e
                return
    
        # If no errors were captured, update validator status
        self.cleaned = True
