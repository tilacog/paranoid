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


class AuditRunnerUnitTest(TestCase): # TODO
    pass

class JobUpdaterUnitTest(TestCase): # TODO
    pass


class ProcessJobUnitTest(TestCase):
    """
    Unit tests for the `process_job` celery task
    """

    def setUp(self):
        ## Patch jobs.Job
        job_patcher = patch('jobs.tasks.Job')
        self.addCleanup(job_patcher.stop)
        self.mock_job = job_patcher.start()

        ## Patch celery.group
        group_patcher = patch('jobs.tasks.group')
        self.addCleanup(group_patcher.stop)
        self.mock_group = group_patcher.start()

        # Isolate return values from celery.group
        mock_grouped_task = self.mock_group.return_value
        self.mock_async_result = mock_grouped_task.delay.return_value

        ## Patch jobs.tasks.update_documents
        update_docs_patcher = patch('jobs.tasks.update_documents')
        self.addCleanup(update_docs_patcher.stop)
        self.mock_update_documents = update_docs_patcher.start()

        ## Patch jobs.tasks.update_job
        update_job_patcher = patch('jobs.tasks.update_job')
        self.addCleanup(update_job_patcher.stop)
        self.mock_update_job = update_job_patcher.start()

        ## Patch jobs.tasks.run_audit
        run_audit_patcher = patch('jobs.tasks.run_audit')
        self.addCleanup(run_audit_patcher.stop)
        self.mock_run_audit = run_audit_patcher.start()

    def test_document_validation_is_called(self):

        process_job(1)  # magic number

        self.mock_async_result.get.called_once_with(propagate=False)

    def test_updates_status_of_invalid_documents_and_job(self):
        """
        On the face of invalid documents, each invalid document must have
        their status updated, and so must be the job instance's state.
        """
        # Create some fake errors
        errors = [DocumentFormatError(pk) for pk in range(3)]
        errors += [DocumentTypeError(pk) for pk in range(2)]

        # Mock celery.group so that it returns those errors
        self.mock_async_result.get.return_value = errors

        # Call the task
        process_job(1)  # magic number

        # Check if update_documents was called with the right collection
        # of errors
        self.mock_update_documents.assert_called_once_with(errors=errors)

        # Check if update_job was called also.
        self.mock_update_job.assert_called_once_with(invalid_documents=True)

    def test_run_audit_isnt_called_if_invalid_documents(self):
        # Create a fake validation error for a document of pk=1
        error = ValidationError(1)

        # Mock celery.group so that it returns those errors
        self.mock_async_result.get.return_value = [error]

        # Call the task
        process_job(1)  # magic number

        # Check if run_audit was not called
        assert not self.mock_run_audit.delay.called, (
            "run_audit should not have been called"
        )

    def test_audit_run_was_called_if_documents_are_okay(self):
        # Mock an audit
        mock_audit = Mock(name='MockAudit', pk=1)
        mock_job =  self.mock_job.objects.get.return_value
        mock_job.audit = mock_audit

        # Call the task
        process_job(1)  # magic number

        # Check if run_audit was called with job.audit.pk
        self.mock_run_audit.delay.assert_called_once_with(audit_pk=mock_audit.pk)

    def test_jobs_are_updated_as_success_on_audit_success(self):
        # Call the task
        process_job(1)  # magic number

        # Check if update_job was called with a success indicator
        self.mock_update_job.assert_called_once_with(success=True)

    def test_jobs_are_updated_as_system_failure_on_audit_error(self):
        pass
