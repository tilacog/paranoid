from django.http import HttpResponse
from django.shortcuts import render

from jobs.models import Job


def new_job(request, job_pk):
    job = Job.objects.get(pk=job_pk) 
    return render(request, 'new_job.html', {'job': job})
