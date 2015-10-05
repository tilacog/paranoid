from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)


class PlainTextValidator(DocumentValidatorProvider):

    def validate(self, file_obj):
       "Assert file has at least one line"
       line = file_obj.readline()
       if not line:
           raise ValidationError
