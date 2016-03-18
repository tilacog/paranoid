from django.shortcuts import render
from django.http import HttpResponse

from .forms import OptInForm


def landing(request):
    form = OptInForm()
    return render(request, 'landing.html', {'form': form})


def receive_squeezejob(request):
    return HttpResponse()
