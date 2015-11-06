from runner.data_processing import AuditRunnerProvider
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)


class DummyValidator(DocumentValidatorProvider):
    """Always accepts documents.
    """
    def validate(self, file_obj):
        pass
