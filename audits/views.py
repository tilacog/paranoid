from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return render(HttpResponse(), 'home.html')
