from django.forms import widgets, ModelForm

from audits.models import Document


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('file', 'doctype')
        widgets = {
            'doctype': widgets.HiddenInput(),
        }
