from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render

from .forms import LoginForm


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        user = form.user_cache
        login(request, user)
        return HttpResponse()
    else:
        return render(request, 'login.html', {'form': form})
