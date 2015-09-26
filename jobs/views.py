from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from jobs.models import Job

@login_required
def new_job(request, job_pk):
    job = Job.objects.get(pk=job_pk)
    return render(request, 'new_job.html', {'job': job})

@login_required
def job_list(request):
    jobs = request.user.job_set.all()
    return render(request, 'job_list.html', {'jobs': jobs})
