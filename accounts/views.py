from django.shortcuts import render

from .forms import LoginForm


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

