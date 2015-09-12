from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from accounts.authentication import ParanoidAuthenticationBackend
User = get_user_model()


class AuthenticateTest(TestCase):
    def setUp(self):
        User.objects.create_user(email='a@b.com', password='top_secret')
        self.backend = ParanoidAuthenticationBackend()

    def test_can_authenticate_valid_user(self):
        user = self.backend.authenticate(email='a@b.com', password='top_secret')
        self.assertIsNotNone(user)

    def test_wont_authenticate_user_with_wrong_password(self):
        user = self.backend.authenticate(email='a@b.com', password='')
        self.assertIsNone(user)

    def test_wont_authenticate_inexisting_user(self):
        user = self.backend.authenticate(email='idont@exist.com', password='123')
        self.assertIsNone(user)

class AuthenticateIntegratedTest(TestCase):

    def test_django_contrib_auth_works(self):
        "Django must know how to authenticate our custom user model"
        User.objects.create_user(email='a@b.com', password='top_secret')
        user = authenticate(email='a@b.com', password='top_secret')
        self.assertIsNotNone(user)
