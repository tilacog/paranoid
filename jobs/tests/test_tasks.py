from unittest import TestCase
from unittest.mock import Mock, patch

from jobs.factories import JobFactory
from jobs.tasks import process_job, validate_document
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)


class JobTaskUnitTest(TestCase):

    def setUp(self):
        ## Patch Document model class and instance
        doc_patcher = patch('jobs.tasks.Document.objects.get')
        self.addCleanup(doc_patcher.stop)
        self.mock_doc_get = doc_patcher.start()

        # Create mocks for validator name
        self.mock_doc = Mock(name='DocumentMock')
        self.mock_doc_get.return_value = self.mock_doc
        self.mock_doc.pk = 1
        self.mock_doc.doctype.validator = 'dummy validator'

        ## Patch DocumentValidatorProvider class and plugins
        provider_patcher = patch('jobs.tasks.DocumentValidatorProvider')
        self.addCleanup(provider_patcher.stop)
        self.mock_provider = provider_patcher.start()

        # Create a mock validator
        self.mock_validator = Mock(name='ValidatorMock')
        self.mock_validator.__name__='dummy validator'
        self.mock_provider.plugins = [self.mock_validator]

    def test_validate_document_gets_the_right_document(self):
        validate_document(self.mock_doc.pk)
        self.mock_doc_get.assert_called_once_with(pk=self.mock_doc.pk)

    def test_validate_document_gets_the_right_validator(self):
        validate_document(self.mock_doc.pk)
        self.mock_validator.assert_called_once_with(self.mock_doc.pk)

    def test_validate_document_returns_OK_on_valid_document(self):
        result = validate_document(self.mock_doc.pk)
        self.assertEqual('OK', result)

    def test_validate_document_returns_ERROR_on_invalid_document(self):
        self.mock_validator.side_effect = ValidationError
        result = validate_document(self.mock_doc.pk)
        self.assertEqual('ERROR', result)

    def test_run_audit_task(self):
        pass

    def test_update_job_task(self):
        pass
