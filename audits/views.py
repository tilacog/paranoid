from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.forms.formsets import formset_factory

from audits.models import Audit
from audits.forms import DocumentForm


@login_required
def home_page(request):
    audits = Audit.objects.all()
    return render(request, 'home.html', {'audits': audits})

def audit_page(request, audit_id):
    audit = Audit.objects.get(id=audit_id)
    DocumentFormSet = formset_factory(DocumentForm, max_num=0)

    if request.method == 'GET':

        initial_data = [
            {'doctype': obj.id}
            for obj in audit.required_doctypes.all()
        ]
        formset = DocumentFormSet(initial=initial_data)

        # Update forms labels to match doctype name
        for form in formset.forms:
            doctype_id = form.initial['doctype']
            doctype_name = audit.required_doctypes.get(id=doctype_id).name
            form.fields['file'].label = doctype_name

        return render(
            request, 'audit.html', {'audit': audit, 'formset': formset}
        )

    elif request.method == 'POST':
        DocumentFormSet = formset_factory(DocumentForm, max_num=0)
        formset = DocumentFormSet(request.POST, request.FILES)

        return render(
            request, 'audit.html', {'audit': audit, 'formset': formset}
        )
