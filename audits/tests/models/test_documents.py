from django.test import TestCase
from unittest.mock import Mock, patch
from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile

from audits.models import Document, Doctype
from django.contrib.auth import get_user_model
User = get_user_model()

class DocumentTest(TestCase):

    def test_can_create_a_minimal_document(self):
        "Document should be created with only the required fields"
        doctype = Doctype.objects.create(name='manad')

        user = User.objects.create_user(email='test@user.com', password='123')
        test_file = SimpleUploadedFile('test_file.txt', b'test file contents')

        document = Document()
        document.doctype = doctype
        document.uploaded_by = user
        document.file = test_file

        document.full_clean()  # should not raise
        document.save()        # should not raise

    # Future tests
    @skip('not a priority right now')
    def test_checksum_is_calculated_before_save(self):
        pass

    @skip('not a priority right now')
    def test_prevent_creating_identical_files(self):
        """
        Upon a duplicated file CREATE request, ignore the file and just
        point the .file attribute to the old, existing filepath.

        It's like a lazy uniqueness constraint, defined at the model cleanup
        phase [?]
        """
        pass


