import types
from unittest import skip
from unittest.mock import DEFAULT, Mock, mock_open, patch

from django.test import TestCase, override_settings

from runner.data_processing import AuditRunnerProvider
from runner.document_validation import (DocumentTypeError,
                                        DocumentValidatorProvider)


class BaseClassTest(TestCase):

    def setUp(self):
        # Reset base class registered subclasses
        DocumentValidatorProvider.plugins = {}

    def tearDown(self):
        # Reset base class registered subclasses
        DocumentValidatorProvider.plugins = {}

    def test_subclasses_are_registered(self):

        # No subclass is registered at the begining
        self.assertEqual(DocumentValidatorProvider.plugins, {})

        # Create a subclass
        class test_class(DocumentValidatorProvider):
            pass

        # Now subclass must be registered
        self.assertDictEqual(
            {'test_class': test_class},
            DocumentValidatorProvider.plugins
        )


class DocumentValidatorProviderTest(TestCase):

    def setUp(self):
        # Patch apps.get_model to return a mock of audits.Document
        patcher = patch('runner.document_validation.apps.get_model')
        self.addCleanup(patcher.stop)
        self.mock_get_model = patcher.start()
        self.mock_doc_cls = self.mock_get_model.return_value

        # Mock Document instance
        self.mock_doc = self.mock_doc_cls.objects.get.return_value
        self.mock_doc.pk = 1
        self.mock_doc.doctype.mime = 'text/plain'
        self.mock_doc.file.url = 'foo'

    @override_settings(MEDIA_ROOT='/fake-media-path/')
    @patch('runner.document_validation.magic', autospec=True)
    def test_can_check_mime(self, mock_magic):
        # Set return value to match mock doctype's
        mock_magic.from_file.return_value = 'text/plain'
        expected_file_path = '/fake-media-path/' + self.mock_doc.file.url

        dvp = DocumentValidatorProvider(1)
        dvp._check_type()

        mock_magic.from_file.assert_called_with(
            expected_file_path,
            mime=True,
        )

    @patch('runner.document_validation.magic', autospec=True)
    def test_can_detect_invalid_mime(self, mock_magic):
        """
        If given an invalid document, Validator should raise an exception
        containing the document pk.
        """
        # Create mocks and fakes
        fake_document_pk = 1
        mock_magic.from_file.return_value = 'invalid/mime'

        # Run validation
        dvp = DocumentValidatorProvider(fake_document_pk)

        # Check if raises the right exception
        with self.assertRaises(DocumentTypeError) as cm:
            dvp._check_type()

        # Check if exception contais document_pk
        self.assertEqual(cm.exception.args, (fake_document_pk,))

    @patch.multiple(DocumentValidatorProvider, _check_type=DEFAULT,
                    validate=DEFAULT)
    def test_can_dispatch_validation(self, _check_type, validate):
        """
        Validator must call two methods: one to check file type and another to
        run the main validation.
        """
        # Patch `open` built-in on target module
        m = mock_open()
        import runner.document_validation
        with patch.object(runner.document_validation, 'open', m, create=True):

            # Create a mock file (for the context manager)
            mock_file = m.return_value

            # Create an abstract validator instance
            # (it's ok since it's methods are mocked)
            validator = DocumentValidatorProvider(1)
            validator.run()

            # assert the two required methods were called
            _check_type.assert_called_with()
            validate.assert_called_with(mock_file)


class AuditRunnerTestCase(TestCase):  # TODO

    def setUp(self):

        # Mock shutil
        shutil_patcher = patch('runner.data_processing.shutil')
        self.addCleanup(shutil_patcher.stop)
        self.mock_shutil = shutil_patcher.start()

        # Patch audit runner instance in order to silence its initialization
        # errors regarding having a concrete `file_manager` object.
        self.mock_file_manager= Mock(spec=types.FunctionType)
        file_manager_patcher = patch.object(
            AuditRunnerProvider,
            'file_manager',
            new=self.mock_file_manager,
            create=True,
        )
        self.addCleanup(file_manager_patcher.stop)
        self.mock_file_manager = file_manager_patcher.start()

        # Use this runner implementation for the next tests
        fake_job_pk = 1
        self.runner = AuditRunnerProvider(fake_job_pk)

    def test_run_calls_anciliary_methods(self):
        """
        runner.run must call `organize_files` and `process_data`
        """
        with patch.multiple(self.runner, organize_files=DEFAULT,
                            process_data=DEFAULT, get_persistent_path=DEFAULT):

            self.runner.run()

            self.runner.organize_files.assert_called_once_with()
            self.runner.process_data.assert_called_once_with()
            self.runner.get_persistent_path.assert_called_once_with(
                self.runner.process_data.return_value
            )

    def test_organize_files_dispatches_file_manager_function(self):

        # Use a fake return value to avoid runtime errors
        self.mock_file_manager.return_value = {'fake': 'files'}

        self.runner.organize_files()
        self.mock_file_manager.assert_called_once_with()

    def test_provides_files_at_runtime(self):
        """
        At audit runtime, the runner instance must have a `self.files`
        attribute.
        """
        self.runner.organize_files()
        self.assertEqual(
            self.runner.files,
            self.mock_file_manager.return_value
        )

    @skip('not a priority right now')
    def test_organize_files_handles_errors_from_file_manager(self):
        pass


    @patch('runner.data_processing.TemporaryDirectory')
    def test_provides_temporary_workspace_at_runtime(self, mock_tempdir):
        """
        A temporary directory must be created and assigned to runner.workspace
        at audit runtime.
        """
        # Mocks for the TemporaryDirectory context manager
        enter_handler = mock_tempdir.return_value.__enter__
        exit_handler = mock_tempdir.return_value.__exit__

        with patch.multiple(
            self.runner,
            organize_files=DEFAULT,
            process_data=DEFAULT,
            get_persistent_path=DEFAULT
        ):
            # Inject an assertion about runner.workspace state, to be verified
            # when runner.process_data gets called.
            self.runner.process_data.side_effect = (
                lambda: self.assertEqual(
                    self.runner.workspace,
                    enter_handler.return_value,  # this is the tempdir path
                    "runner.workspace must point to a tempdir at runtime"
                )
            )

            self.runner.run()

        # Assert TemporaryDirectory was called as a context manager
        enter_handler.assert_called_once_with()
        exit_handler.assert_called_once_with(None, None, None)


    def test_report_file_is_persisted_elsewhere(self):
        """
        `shutil.move` must be called using the filepath returned from the
        `process_data` method.
        """
        mock_process_data = Mock(return_value='old_file_path')
        mock_get_persistent_path = Mock(return_value='new_file_path')
        with patch.multiple(
            self.runner,
            organize_files=DEFAULT,
            process_data=mock_process_data,
            get_persistent_path=mock_get_persistent_path,
        ):
            self.runner.run()

        self.mock_shutil.move.assert_called_once_with(
            src=mock_process_data.return_value,
            dst=mock_get_persistent_path.return_value
        )

    def test_runner_keeps_reference_to_report_path(self):
        """
        At the end of the data processing, the runner instance should keep
        a reference to the final report (final) path.
        """
        mock_process_data = Mock(return_value='old_file_path')
        mock_get_persistent_path = Mock(return_value='new_file_path')
        with patch.multiple(
            self.runner,
            organize_files=DEFAULT,
            process_data=mock_process_data,
            get_persistent_path=mock_get_persistent_path,
        ):
            self.runner.run()

        self.assertEqual(
            self.runner.report_path,
            mock_get_persistent_path.return_value
        )


class ConcreteAuditRunnerTest(TestCase):
    """
    Tests for minimal audit runner implementations
    """

    def test_cant_instantiate_without_file_manager(self):
        class TestAudit(AuditRunnerProvider):
            # file_manager is absent
            pass

        with self.assertRaises(TypeError):
            fake_job_pk = 1
            TestAudit(fake_job_pk)
