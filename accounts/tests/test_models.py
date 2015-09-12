from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest import skip

User = get_user_model()

class UserModelTest(TestCase):

    def setUp(self):
        self.user_data = {
            'first_name': 'john',
            'last_name': 'lennon',
            'email': 'john@beatles.com',
            'password': 'allyouneedislove',
        }

    def test_user_is_valid_without_username_field(self):
        user = User(**self.user_data)
        user.full_clean()  # should not raise

    def test_user_can_be_created_with_email_and_password_only(self):
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
        )


    def test_email_is_primary_key(self):
        user = User()
        self.assertFalse(hasattr(user, 'id'))

    def test_is_authenticated(self):
        user = User()
        self.assertTrue(user.is_authenticated())

