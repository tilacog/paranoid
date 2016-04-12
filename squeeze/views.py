from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from jobs.views import build_download_response
from squeeze.forms import OptInForm, get_beta_user
from squeeze.models import SqueezeJob


def landing(request):
    form = OptInForm()
    return render(request, 'landing.html', {'form': form})


def receive_squeezejob(request):
    # Only answers to POST requests
    if request.method == 'GET':
        return HttpResponse(status=405)

    form = OptInForm(request.POST, request.FILES)
    if form.is_valid():
        squeezejob = form.save()
        return redirect('success_optin', squeezejob.random_key)
    else:
        # TODO: Return to landing page with errors
        return HttpResponse(400)


def success_optin(request, uid):
    squeezejob = get_object_or_404(SqueezeJob, random_key=uid)
    return render(request, 'success.html', {'squeezejob': squeezejob})

def download_squeezejob(request, uid):
    """Downloads file or redirects if download link is expired.
    """
    squeezejob = get_object_or_404(SqueezeJob, random_key=uid)
    if squeezejob.is_expired:
        return redirect('expired_download_link')

    job = squeezejob.job
    beta_user = get_beta_user()
    response = build_download_response(job.pk, beta_user)

    return response

def expired_download_link(request):
    return render(request, 'expired.html')
