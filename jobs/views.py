from django.shortcuts import render
from django.http import HttpResponse

def new_job(request, job_pk):
    return render(request, 'new_job.html')
