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
    user = authenticate(
        email=request.POST.get('email'),
        password=request.POST.get('password')
    )

    if user:
        login(request, user)
        return HttpResponse()
    return HttpResponse(status=422)
