from django.shortcuts import render
from django.http import HttpResponse

def job_received(request, job_pk):
    return render(request, 'job_received.html')
