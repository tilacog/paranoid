from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {'password': forms.PasswordInput}
