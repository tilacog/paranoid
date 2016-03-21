from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse

from .forms import OptInForm
from .models import SqueezeJob


def landing(request):
    form = OptInForm()
    return render(request, 'landing.html', {'form': form})


def receive_squeezejob(request):

    # Olny answers to POST requests
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
