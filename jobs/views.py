from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from jobs.models import Job


@login_required
def new_job(request, job_pk):
    job = Job.objects.get(pk=job_pk)
    return render(request, 'new_job.html', {'job': job})

@login_required
def job_list(request):
    jobs = request.user.job_set.all()
    return render(request, 'job_list.html', {'jobs': jobs})

@login_required
def download_report(request, job_pk):
    """
    Let nginx Accell Redirect handle file downloads.
    """

    # Someday this will change in order to enable group sharing of reports.
    job = get_object_or_404(Job, pk=job_pk, user=request.user)

    # Let nginx handle file downloads
    response = HttpResponse()
    response['Content-Type'] = ''

    file_extension = job.report_file.name.split('.')[-1]
    file_name = "Report #{num}.{ext}".format(
        num=job.pk,
        ext=file_extension,
    )

    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        file_name,
    )

    response['X-Accel-Redirect'] = "/protected/{}".format(
        job.report_file.path.split('/media/')[-1]
    )
    return response
