from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

EMPTY_EMAIL_ERROR = 'Informe um email válido'
EMPTY_PASSWORD_ERROR = 'Informe uma senha'


class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class':'form-control',
                'placeholder': 'Email',
            }),

            'password': forms.PasswordInput(attrs={
                'class':'form-control',
                'placeholder': 'Senha',
            }),
        }

        error_messages = {
            'email': {'required': EMPTY_EMAIL_ERROR},
            'password': {'required': EMPTY_PASSWORD_ERROR}
        }
