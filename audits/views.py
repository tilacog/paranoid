from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms.formsets import formset_factory

from audits.models import Audit
from audits.forms import DocumentForm, DocumentFormSet


@login_required
def home_page(request):
    audits = Audit.objects.all()
    return render(request, 'home.html', {'audits': audits})

def audit_page(request, audit_pk):
    audit = Audit.objects.get(id=audit_pk)

    if request.method == 'POST':
        formset = DocumentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(request.user.pk)
            return redirect('job_received', 1)

    if request.method == 'GET':
        formset = DocumentFormSet(audit_pk=audit_pk)

    return render(
        request, 'audit.html', {'audit': audit, 'formset': formset}
    )
