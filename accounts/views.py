from django.shortcuts import render

from .forms import LoginForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)

    return render(request, 'login.html', {'form': form})
