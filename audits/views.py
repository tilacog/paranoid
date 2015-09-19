from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.forms.formsets import formset_factory

from audits.models import Audit
from audits.forms import DocumentForm


@login_required
def home_page(request):
    return render(request, 'home.html')


def audit_page(request, audit_id):
    audit = Audit.objects.get(id=audit_id)
    DocumentFormset = formset_factory(DocumentForm)
    initial_data = [
        {'doctype': obj.id} for obj in audit.required_doctypes.all()
    ] 
    formset = DocumentFormset(initial=initial_data)
    return render(request, 'audit.html', {'audit': audit, 'formset': formset})
