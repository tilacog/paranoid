from django.forms import ModelForm 
from django.forms.widgets import HiddenInput

from audits.models import Document


class DocumentForm(ModelForm):
    class Meta:
        model = Document 
        fields = ('file', 'doctype')
        widgets = {
            'doctype': HiddenInput()
        }
