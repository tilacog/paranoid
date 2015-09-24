from django.contrib.auth import get_user_model
from django.forms import ModelForm, widgets
from django.forms.formsets import BaseFormSet, formset_factory

from audits.models import Audit, Doctype, Document

User = get_user_model()

class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('file', 'doctype')
        widgets = {
            'doctype': widgets.HiddenInput(),
        }


class DocumentBaseFormSet(BaseFormSet):
    """
    A formset that tries to use an audit instance to generate its own initial
    data and update it's forms labels.
    """

    def __init__(self, *args, **kwargs):
        """
        Check if an optional ``audit_pk`` kwarg was passed on initialization.
        If positive, the formset will generate it's own initial data and
        update his forms labels according to each doctype related to the
        audit.
        """
        audit_pk = kwargs.pop('audit_pk', None)
        if audit_pk:
            self.audit = Audit.objects.get(pk=audit_pk)
            init_data = self._create_initial_data()
            super().__init__(*args, initial=init_data, **kwargs)
            self._update_labels()

        else:
            super().__init__(*args, **kwargs)

    def _create_initial_data(self):
        """Create one form per docytpe in audit.related_doctypes."""
        init_data = [
            {'doctype': obj.pk}
            for obj in self.audit.required_doctypes.all()
        ]
        return init_data

    def _update_labels(self):
        """Update each form labels to match doctype's name."""
        for form in self.forms:
            doctype_pk = form.initial['doctype']
            doctype_name = self.audit.required_doctypes.get(pk=doctype_pk).name
            form.fields['file'].label = doctype_name

    def save(self, user_pk):
        if not self.is_valid():
            raise RuntimeError('Formset has invalid data. Cannot save.')

        new_documents = []
        for form in self.forms:
            user = User.objects.get(pk=user_pk)
            doctype = form.cleaned_data['doctype']
            file_obj = form.cleaned_data['file']
            new_documents.append(Document(user=user, doctype=doctype, file=file_obj))

        Document.objects.bulk_create(new_documents)


# This formset should be used on views
DocumentFormSet = formset_factory(
    DocumentForm,
    formset=DocumentBaseFormSet,
    max_num=0
)
