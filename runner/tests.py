import types
from unittest import skip
from unittest.mock import DEFAULT, Mock, mock_open, patch

from django.test import TestCase, override_settings

from runner.data_processing import AuditRunnerProvider
from runner.document_validation import DocumentValidatorProvider

class BaseClassTest(TestCase):

    def tearDown(self):
        # Remove inserted classes to preserve test isolation
        DocumentValidatorProvider.plugins.pop('test_class')

    def test_subclasses_are_registered(self):

        # Subclass isn't registered at the begining
        self.assertNotIn(
            'test_class',
            DocumentValidatorProvider.plugins.keys()
        )

        # Create a subclass
        class test_class(DocumentValidatorProvider):
            pass

        # Now subclass is registered
        self.assertEqual(
            test_class,
            DocumentValidatorProvider.plugins['test_class']
        )


class DocumentValidatorProviderTest(TestCase):

    def setUp(self):
        self.initial_data = ('/fake/path', 'fake_mime', 'fake_encoding')

    @patch('runner.document_validation.magic', autospec=True)
    def test_can_check_mime(self, mock_magic):
        "Validator must call `magic.from_file` using it's file_path attribute"

        validator = DocumentValidatorProvider(*self.initial_data)
        validator._has_right_type()

        mock_magic.from_file.assert_called_once_with(
            self.initial_data[0],
            mime=True,
        )

    @patch('runner.document_validation.magic', autospec=True)
    def test_can_detect_invalid_mime(self, mock_magic):
        """
        If given an invalid document `validator.has_right_type` method should
        return False
        """

        # magic.from_file return bytes
        mock_magic.from_file.return_value = b'invalid/mime'

        # Run validation
        validator = DocumentValidatorProvider(*self.initial_data)

        result = validator._has_right_type()
        self.assertFalse(result)

    @patch.multiple(DocumentValidatorProvider, _has_right_type=DEFAULT,
                    validate=DEFAULT)
    def test_can_dispatch_validation(self, _has_right_type, validate):
        """
        Validator must call methods to check the file type and format.
        """
        # Patch `open` built-in on target module
        m = mock_open()
        import runner.document_validation
        with patch.object(runner.document_validation, 'open', m, create=True):

            # Create a mock file (for the context manager)
            mock_file_pointer = m.return_value

            validator = DocumentValidatorProvider(*self.initial_data)
            validator.run()

            # Assert that the required methods were called
            _has_right_type.assert_called_once_with()
            validate.assert_called_with(mock_file_pointer)

    @skip
    def test_validation_results(self):  # TODO
        pass


class AuditRunnerTestCase(TestCase):

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

        # Patch AuditRunner's extension attribute
        ext_patcher = patch.object(
            AuditRunnerProvider,
            'extension',
            new='test',
            create=True,
        )
        self.addCleanup(ext_patcher.stop)
        self.mock_extension = ext_patcher.start()

        # Use this runner implementation for the next tests
        self.initial_data = [('doctype1','file/path/1'),('doctype2','file/path/2')]
        self.runner = AuditRunnerProvider(self.initial_data)


    def test_instantiation(self):
        """
        Concrete runner should be instantiated with a raw file list,
        which will be stored at `self.raw_files`
        """
        self.assertEqual(
            self.initial_data,
            self.runner.raw_files
        )


    def test_run_calls_anciliary_methods(self):
        "runner.run must call a series of anciliary methods"

        # patch anciliary methods
        with patch.multiple(self.runner, organize_files=DEFAULT,
                            process_data=DEFAULT, post_process=DEFAULT):

            self.runner.run()

            # Check calls on anciliary methods
            self.runner.organize_files.assert_called_once_with()
            self.runner.process_data.assert_called_once_with()
            self.runner.post_process.assert_called_once_with()

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
        `shutil.move` must be called using the filepath from runner.output
        and runner.report_path.
        """
        mock_output = Mock(return_value='new_file_path')
        with patch.multiple(
            self.runner,
            organize_files=DEFAULT,
            process_data=DEFAULT,
        ):
            self.runner.run()

        self.mock_shutil.move.assert_called_once_with(
            src=self.runner.output,
            dst=self.runner.report_path
        )

    def test_runner_keeps_reference_to_report_path(self):
        """
        The runner instance keeps a reference to the report final after the
        data processing phase.
        """
        with patch.multiple(self.runner, organize_files=DEFAULT,
                            process_data=DEFAULT):

            self.assertIsNone(self.runner.report_path)
            self.runner.run()
            self.assertIsNotNone(self.runner.report_path)


class ConcreteAuditRunnerTest(TestCase):
    """
    Tests for minimal audit runner implementations
    """

    def setUp(self):
        self.initial_data = [('doctype','fake_path')]

    def test_cant_instantiate_without_file_manager_or_extension(self):
        "Trying to instantiate a concrete runner should raise a TypeError"

        NoFileMgr= type('NoFileMgr', (AuditRunnerProvider,),
                        {'extension':'X'})

        NoExt = type('NoExt', (AuditRunnerProvider,),
                     {'file_manager':lambda x:x})

        with self.assertRaises(TypeError):
            NoFileMgr(self.initial_data)
            NoExt(self.initial_data)

        # The following should not raise
        OkAuditRunner = type('OkAuditRunner', (AuditRunnerProvider,),
                             {'file_manager': lambda x:x,
                              'extension': 'txt'})

        # Remove inserted classes to preserve test isolation
        AuditRunnerProvider.plugins.pop('NoFileMgr')
        AuditRunnerProvider.plugins.pop('NoExt')
        AuditRunnerProvider.plugins.pop('OkAuditRunner')
