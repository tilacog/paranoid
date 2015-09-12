from django.contrib.auth import get_user_model
User = get_user_model()

class ParanoidAuthenticationBackend:

    def authenticate(self, email, password):
        user = self.get_user(email)
        if not user or not user.check_password(password):
            return None
        return user


    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
