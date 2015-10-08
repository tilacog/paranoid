from unittest import TestCase
from unittest.mock import Mock, patch

from jobs.factories import JobFactory
from jobs.tasks import process_job, validate_document
from runner.document_validation import (DocumentFormatError, DocumentTypeError,
                                        DocumentValidatorProvider,
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

        # Create a mock validator class
        self.mock_validator_cls = Mock(name='MockValidatorClass')
        self.mock_validator_cls.__name__='dummy validator'
        self.mock_provider.plugins = [self.mock_validator_cls]

        # Create a mock validator instance
        self.mock_validator = Mock(name='MockValidatorInstance')
        self.mock_validator.error = None  # raise no errors by default
        self.mock_validator_cls.return_value = self.mock_validator

    def test_can_fetch_the_right_document(self):
        validate_document(self.mock_doc.pk)
        self.mock_doc_get.assert_called_once_with(pk=self.mock_doc.pk)

    def test_calls_validator_run_method(self):
        validate_document(self.mock_doc.pk)
        self.mock_validator.run.assert_called_once_with()

    def test_propagates_errors_with_document_pk(self):
        # Check if propagates DocumentTypeErrors
        self.mock_validator.error = DocumentTypeError(self.mock_doc.pk)
        with self.assertRaises(DocumentTypeError) as cm1:
            validate_document(self.mock_doc.pk)
        self.assertEqual(cm1.exception.args, (self.mock_doc.pk,))

        # Check if propagates DocumentTypeErrors
        self.mock_validator.error = DocumentFormatError(self.mock_doc.pk)
        with self.assertRaises(DocumentFormatError) as cm2:
            validate_document(self.mock_doc.pk)
        self.assertEqual(cm2.exception.args, (self.mock_doc.pk,))


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
    @patch('jobs.tasks.update_documents')
    def test_updates_status_of_invalid_documents(
        self,
        mock_update_documents,
        mock_group
    ):

        # Create some fake errors
        errors = [DocumentFormatError(pk) for pk in range(3)]
        errors += [DocumentTypeError(pk) for pk in range(2)]

        # Mock celery.group so that it returns those errors
        mock_grouped_task = mock_group.return_value
        mock_async_result = mock_grouped_task.delay.return_value
        mock_async_result.get.return_value = errors

        result = process_job(1)  # magic number

        # Check if update_documents was called with the right collection
        # of errors
        mock_update_documents.delay.assert_called_once_with(errors=errors)
