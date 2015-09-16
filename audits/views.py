from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from audits.models import Audit


@login_required
def home_page(request):
    return render(request, 'home.html')


def audit_page(request, audit_id):

    audit = Audit.objects.get(id=audit_id)
    return render(request, 'audit.html', {'audit': audit})
