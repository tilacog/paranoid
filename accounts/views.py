from django.shortcuts import render

from .forms import LoginForm


def login_view(request):
    form = LoginForm(data=request.POST)  # on GET form will still be blank
    return render(request, 'login.html', {'form': form})
