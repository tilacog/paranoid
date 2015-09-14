from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

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
        return redirect(reverse('home_page'))
    else:
        return render(request, 'login.html', {'form': form})
