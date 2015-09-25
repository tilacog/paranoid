from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


EMPTY_EMAIL_ERROR = "Por favor, digite um email"
EMPTY_PASSWORD_ERROR = "Por favor, digite uma senha"
INVALID_LOGIN_ERROR = "Usuário ou senha incorreto."
INACTIVE_USER_ERROR = "Esta conta está desativada."

class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }),

            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Senha',
            }),
        }

        error_messages = {
            'invalid_login': INVALID_LOGIN_ERROR,
            'inactive': INACTIVE_USER_ERROR,
            'email': {'required': EMPTY_EMAIL_ERROR},
            'password': {'required': EMPTY_PASSWORD_ERROR},
        }

    def __init__(self, *args, **kwargs):
        # Create a placeholder for the user instance
        self.user_cache = None
        super().__init__(*args, **kwargs)


    def clean(self):
        """
        Checks if user can be authenticated.

        If positive, the user instance is stored in self.user_cache.

        Also checks if user is active.
        """
        email = self.cleaned_data.get('email')
        password= self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.Meta.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.Meta.error_messages['inactive'],
                code='inactive',
            )

    def get_user_email(self):
        if self.user_cache:
            return self.user_cache.email
        return None

    def get_user(self):
        return self.user_cache
