from unittest import TestCase
from unittest.mock import Mock, patch

from jobs.factories import JobFactory
from jobs.tasks import process_job, validate_document
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)


class ValidateDocumentUnitTest(TestCase):

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

    def test_can_fetch_the_right_document(self):
        validate_document(self.mock_doc.pk)
        self.mock_doc_get.assert_called_once_with(pk=self.mock_doc.pk)

    def test_can_fetch_the_right_validator(self):
        validate_document(self.mock_doc.pk)
        self.mock_validator.assert_called_once_with(self.mock_doc.pk)

    def test_raises_error_on_invalid_document(self):
        self.mock_validator.side_effect = ValidationError
        with self.assertRaises(ValidationError):
            validate_document(self.mock_doc.pk)


class AuditRunnerUnitTest(TestCase):
    pass

class JobUpdaterUnitTest(TestCase):
    pass


class ProcessJobTest(TestCase):

    def setUp(self):
        patcher = patch('jobs.tasks.Job')
        self.addCleanup(patcher.stop)
        mock_job = patcher.start()

    @patch('jobs.tasks.group')
    def test_validation_doesnt_propagate_errors(self, mock_group):
        mock_grouped_task = mock_group.return_value
        mock_async_result = mock_grouped_task.delay.return_value

        process_job(1)  # magic number

        mock_async_result.get.called_once_with(propagate=False)

    @patch('jobs.tasks.group')
    def test_returns_pks_of_invalid_documents(self, mock_group):
        # Create some fake document pks for the invalid mocked documents
        invalid_documents_pks = range(3)

        # Mock celery.group so that it returns some validation errors
        mock_grouped_task = mock_group.return_value
        mock_async_result = mock_grouped_task.delay.return_value
        mock_async_result.get.return_value = [
            ValidationError(pk) for pk in invalid_documents_pks
        ]

        result = process_job(1)  # magic number

        # Grab the pks inside each exception arguments and assert they're
        # the excpected pks
        returned_pks = [exception.args[0] for exception in result]
        self.assertEqual(returned_pks, list(invalid_documents_pks))
