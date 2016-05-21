from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render

from audits.forms import DocumentForm, DocumentFormSet
from audits.models import Audit
from jobs.models import Job


@login_required
def home_page(request):
    audits = Audit.objects.all()
    return render(request, 'home.html', {'audits': audits})

@login_required
def audit_page(request, audit_pk):
    audit = Audit.objects.get(id=audit_pk)

    if request.method == 'POST':
        formset = DocumentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            new_docs_pks = formset.save(request.user)
            job = Job.objects.create(audit=audit, user=request.user)
            job.documents.add(*new_docs_pks)
            return redirect(job)

    if request.method == 'GET':
        formset = DocumentFormSet(audit_pk=audit_pk)

    return render(
        request, 'audit.html', {'audit': audit, 'formset': formset}
    )
