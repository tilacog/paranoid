from django.shortcuts import render
from django.http import HttpResponse


def landing(request):
    return render(request, 'landing.html')


def receive_squeezejob(request):
    return HttpResponse()
