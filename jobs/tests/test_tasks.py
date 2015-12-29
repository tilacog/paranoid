import os
from unittest import TestCase, skip
from unittest.mock import Mock, patch

from jobs.models import Job
from jobs.tasks import (prepare_documents, process_job, run_audit, update_job,
                        validate_document)


class ValidateDocumentUnitTest(TestCase):

    def setUp(self):
        # Patch Document model class and instance
        doc_patcher = patch('jobs.tasks.Document')
        self.addCleanup(doc_patcher.stop)
        self.mock_doc_cls= doc_patcher.start()

        # Create mocks for validator name
        self.mock_doc = Mock(name='DocumentMock')
        self.mock_doc.pk = 1
        self.mock_doc.file.name = 'path/to/mock_doc_file'
        self.mock_doc.doctype.encoding = 'utf-8'
        self.mock_doc.doctype.mime = 'text/plain'

        self.mock_doc_cls.objects.get.return_value = self.mock_doc

        # Create a mock validator class/plugin
        self.mock_validator_cls = Mock(name='MockValidatorClass')
        self.mock_doc.doctype.get_validator.return_value = (
            self.mock_validator_cls
        )

        # Create a mock validator instance
        self.mock_validator = Mock(name='MockValidatorInstance')
        self.mock_validator.error = None  # raise no errors by default
        self.mock_validator_cls.return_value = self.mock_validator

    def test_can_fetch_the_right_document(self):
        validate_document(self.mock_doc.pk)
        self.mock_doc_cls.objects.get.assert_called_once_with(pk=self.mock_doc.pk)

    def test_validator_is_instantiated_with_the_right_arguments(self):
        validate_document(self.mock_doc.pk)
        self.mock_validator_cls.assert_called_once_with(
            file_path = os.path.abspath(os.path.join(
                '../media', self.mock_doc.file.name
            )),
            mime=self.mock_doc.doctype.mime,
            encoding=self.mock_doc.doctype.encoding,
        )

    def test_validator_run_method_is_called(self):
        validate_document(self.mock_doc.pk)
        self.mock_validator.run.assert_called_once_with()


class RunAuditUnitTest(TestCase):

    def setUp(self):

        # Patch audits.Audit
        audit_patcher = patch('jobs.tasks.Audit')
        self.addCleanup(audit_patcher.stop)
        self.mock_audit_cls = audit_patcher.start()

        # Mock Audit instance
        self.mock_audit = self.mock_audit_cls.objects.get.return_value
        self.mock_audit.pk = 1
        self.mock_audit.audit_runner = 'dummy audit runner'
        # Patch jobs.Job
        job_patcher = patch('jobs.tasks.Job')
        self.addCleanup(job_patcher.stop)
        self.mock_job_cls = job_patcher.start()

        # Mock Job instance
        self.mock_job = self.mock_job_cls.objects.get.return_value
        self.mock_job.pk = 1
        self.mock_job.audit = self.mock_audit

        # Create a mock AuditRunner class/plugin
        self.mock_runner_cls = Mock(name='MockAuditRunnerClass')
        self.mock_job.audit.get_runner.return_value = self.mock_runner_cls

        # Create a mock runner instance
        self.mock_runner = Mock(name='MockAuditRunnerInstance')
        self.mock_runner_cls.return_value = self.mock_runner

    @patch('jobs.tasks.prepare_documents')
    def test_instantiates_runner(self, mock_prep_docs):
        "Concrete runner must be instantiated using the job's raw files"
        mock_docs = mock_prep_docs.return_value

        run_audit(self.mock_job.pk)

        mock_prep_docs.assert_called_once_with(self.mock_job.pk)
        self.mock_runner_cls.assert_called_once_with(mock_docs)

    def test_calls_runner_run_method(self):
        "Concrete runner `run` method must be called"
        run_audit(self.mock_job.pk)
        self.mock_runner.run.assert_called_once_with()


class PrepareDocumentsUnitTest(TestCase):

    @patch('jobs.tasks.Job')
    def test_returns_job_documents_as_list_of_tuples(self, job_cls):


        mock_document_1 = Mock(name='MockDoc_1')
        mock_document_1.doctype.name = 'MockDoctype_1'
        mock_document_1.file.file.name = 'path/to/file/MockDoc_1'

        mock_document_2 = Mock(name='MockDocument_2')
        mock_document_2.doctype.name = 'MockDoctype_2'
        mock_document_2.file.file.name = 'path/to/file/MockDoc_2'

        mock_job = Mock(name='MockJob')
        mock_job.pk = 1
        mock_job.documents.all.return_value = [mock_document_1, mock_document_2]

        job_cls.objects.get.return_value = mock_job

        expected_output = [
            (mock.doctype.name, mock.file.file.name)
            for mock in [mock_document_1, mock_document_2]
        ]

        docs = prepare_documents(mock_job.pk)

        self.assertEqual(docs, expected_output)

class DocumentUpdaterUnitTest(TestCase):  # TODO
    pass


class JobUpdaterUnitTest(TestCase):

    def setUp(self):
        # Patch jobs.Job
        job_patcher = patch('jobs.tasks.Job')
        self.addCleanup(job_patcher.stop)
        self.mock_job_cls = job_patcher.start()
        self.mock_job_cls.SUCCESS_STATE = Job.SUCCESS_STATE
        self.mock_job_cls.FAILURE_STATE = Job.FAILURE_STATE

        # Mock Job instance
        self.mock_job = Mock(name='MockJob', pk=1)
        self.mock_job_cls.objects.get.return_value = self.mock_job

    def test_can_get_a_job(self):
        update_job(self.mock_job.pk, success=True)
        self.mock_job_cls.objects.get.assert_called_once_with(
            pk=self.mock_job.pk
        )

    def test_can_update_a_job_if_it_has_invalid_documents(self):
        self.mock_job.state = None
        update_job(self.mock_job.pk, invalid_documents=True)
        self.assertEqual(self.mock_job.state, Job.FAILURE_STATE)

        # Checks if model instance was saved afterwards
        self.assertTrue(self.mock_job.save.called)

    def test_can_update_a_job_if_audit_sucessfull(self):
        self.mock_job.state = None
        fake_report_path = '/fake/path/'

        update_job(
            self.mock_job.pk,
            success=True,
            report_path=fake_report_path
        )

        self.assertEqual(self.mock_job.state, Job.SUCCESS_STATE)
        self.assertEqual(self.mock_job.report_file.name, fake_report_path)

        # Checks if model instance was saved afterwards
        self.assertTrue(self.mock_job.save.called)


class ProcessJobUnitTest(TestCase):
    """
    Unit tests for the `process_job` celery task
    """

    def setUp(self):
        # Patch jobs.Job
        job_patcher = patch('jobs.tasks.Job')
        self.addCleanup(job_patcher.stop)
        self.mock_job_cls = job_patcher.start()

        # Patch jobs.tasks.update_documents
        update_docs_patcher = patch('jobs.tasks.update_documents')
        self.addCleanup(update_docs_patcher.stop)
        self.mock_update_documents = update_docs_patcher.start()

        # Patch jobs.tasks.update_job
        update_job_patcher = patch('jobs.tasks.update_job')
        self.addCleanup(update_job_patcher.stop)
        self.mock_update_job = update_job_patcher.start()

        # Patch jobs.tasks.run_audit
        run_audit_patcher = patch('jobs.tasks.run_audit')
        self.addCleanup(run_audit_patcher.stop)
        self.mock_run_audit = run_audit_patcher.start()

    @patch('jobs.tasks.validate_document')
    def test_document_validation_is_called(self, mock_validate):
        mock_job = self.mock_job_cls.objects.get.return_value
        mock_job.pk = 1
        fake_documents_pks = list(range(3))
        mock_job.documents.all.return_value = [
            Mock(pk=i) for i in fake_documents_pks
        ]

        process_job(mock_job.pk)

        self.assertEqual(len(fake_documents_pks), mock_validate.call_count)
        for i in fake_documents_pks:
            mock_validate.assert_any_calls(i)

    @patch('jobs.tasks.validate_document')
    def test_updates_status_of_invalid_documents_and_job(self, mock_validate):
        """
        On the face of invalid documents, each invalid document must have
        their status updated, and so must be the job instance's state.
        """
        mock_job = Mock(pk=1)
        mock_job.documents.all.return_value = [Mock()]
        self.mock_job_cls.objects.get.return_value = mock_job

        error = {'error': 'ValidationError', 'pk': mock_job.pk}
        mock_validate.return_value = error

        # Call the task
        process_job(mock_job.pk)

        # Check if update_documents was called with the right collection
        # of errors
        self.mock_update_documents.assert_called_once_with(errors=[error])

        # Check if update_job was called also.
        self.mock_update_job.assert_called_once_with(
            mock_job.pk,
            invalid_documents=True
        )

    @patch('jobs.tasks.validate_document')
    def test_run_audit_isnt_called_if_invalid_documents(self, mock_validate):
        mock_job = Mock(pk=1)
        mock_validate.return_value = {
            'error': 'ValidationError',
            'pk': mock_job.pk
        }

        # Call the task
        process_job(mock_job.pk)

        # Check if run_audit was not called
        assert not self.mock_run_audit.delay.called, (
            "run_audit should not have been called"
        )

    def test_audit_run_was_called_if_documents_are_okay(self):
        # Mock an audit
        mock_job = self.mock_job_cls.objects.get.return_value
        mock_job.pk = 1
        # Call the task
        process_job(mock_job.pk)

        # Check if run_audit was called with job.audit.pk
        self.mock_run_audit.assert_called_once_with(job_pk=mock_job.pk)

    @patch('jobs.tasks.run_audit')
    def test_jobs_are_updated_on_audit_success(self, mock_run_audit):
        """
        Jobs must have their STATE and REPORT_FILE fields updated on audit
        success
        """
        fake_job_pk = 1

        # Call the task
        process_job(fake_job_pk)  # magic number

        # Check if update_job was called with a success indicator
        self.mock_update_job.assert_called_once_with(
            fake_job_pk,
            success=True,
            report_path=mock_run_audit.return_value
        )

    @skip("Haven't decided on how to handle audit errors yet")
    def test_jobs_are_updated_on_audit_error(self):

        pass
