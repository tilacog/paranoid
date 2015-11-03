import os.path

import magic

from runner.plugin_mount import PluginMount


class ValidationError(Exception):
    "To be raised when file format doesn't comply with validation rules"
    pass


class DocumentValidatorProvider(metaclass=PluginMount):
    """
    Mount point for plugins which refer to validations that can be performed.
    Plugins implementing this reference should define the following:

    Init Parameters
    ---------------

     file_path : the absolute path to the file,
     mime : the expected mime type for the file,
     encoding : the encoding to be used when reading the file.

    Methods
    -------
    validate : method
        Override this in subclasses to define the validation logic for the 
        doctype. It takes an open file pointer object as argument, and should
        raise a ValidationError if the file is found to be invalid or simply
        return if not.
    """

    def __init__(self, file_path, mime, encoding):
        self.file_path = file_path
        self.mime = mime
        self.encoding = encoding

    def _has_right_type(self):
        "Check if the document is of the right media type"
        mime = magic.from_file(self.file_path, mime=True)
        if mime.decode() != self.mime:
            return False
        else:
            return True

    def _has_right_format(self, file_pointer):
        "Check if the file has the expected format"
        try:
            self.validate(file_pointer)

        except ValidationError:
            return False

        else:
            return True

    def validate(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def run(self):
        "Perform full validation on document and return a result dict"

        # Perform type validation first
        if not self._has_right_type():
            return {'error': 'invalid type'}

        with open(self.file_path, encoding=self.encoding) as fp:


            # Run format validation while trying to catch invalid encoding
            # exceptions
            try:
                right_format = self._has_right_format(fp)
            except UnicodeDecodeError:
                return {'error': 'invalid encoding'}

            if not right_format:
                return {'error': 'invalid format'}

            # Return no errors if everyting is OK
            return {'error': None}
