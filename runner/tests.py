from unittest.mock import DEFAULT, mock_open, patch

from django.test import TestCase, override_settings

# from runner.data_processing import AuditRunner
from runner.document_validation import (DocumentTypeError,
                                        DocumentValidatorProvider)


class BaseClassTest(TestCase):

    def setUp(self):
        # Reset base class registered subclasses
        DocumentValidatorProvider.plugins = []

    def tearDown(self):
        # Reset base class registered subclasses
        DocumentValidatorProvider.plugins = []

    def test_subclasses_are_registered(self):

        # No subclass is registered at the begining
        self.assertEqual(DocumentValidatorProvider.plugins, [])

        # Create a subclass
        class test_class(DocumentValidatorProvider):
            pass

        # Now subclass must be registered
        self.assertIn(test_class, DocumentValidatorProvider.plugins)


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

    def test_can_be_instantiated(self):
        pass

    def test_can_get_job_files(self):
        pass

    def test_returns_an_existing_file_path(self):
        pass
