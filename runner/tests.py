from unittest.mock import DEFAULT, Mock, patch

from django.test import TestCase, override_settings

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
        patcher = patch('runner.document_validation.apps.get_model', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_get_model = patcher.start()
        self.mock_doc_cls = self.mock_get_model.return_value

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

    @override_settings(MEDIA_ROOT='')
    @patch('runner.document_validation.magic', autospec=True)
    def test_can_detect_invalid_mime(self, mock_magic):
        mock_magic.from_file.return_value = 'invalid/mime'

        dvp = DocumentValidatorProvider(1)

        with self.assertRaises(DocumentTypeError):
            dvp._check_type()

    @patch.multiple(
        DocumentValidatorProvider,
        _check_type=DEFAULT,
        validate=DEFAULT,
    )
    def test_can_dispatch_validation(self, _check_type, validate):

        # Shorter name for the document file context manager
        doc_file_cm = self.mock_doc.file.__enter__.return_value

        dvp = DocumentValidatorProvider(1)
        dvp.run()

        _check_type.assert_called_with()
        validate.assert_called_with(doc_file_cm)
