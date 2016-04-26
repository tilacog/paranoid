from django import forms
from django.contrib import admin

from audits.models import Audit, Doctype, Document, Package
from runner.data_processing import AuditRunnerProvider
from runner.document_validation import DocumentValidatorProvider


AUDIT_RUNNER_CHOICES = ((k, k) for k in AuditRunnerProvider.plugins.keys())


class AuditAdminForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = '__all__'
        widgets = {
            'runner': forms.Select(choices=AUDIT_RUNNER_CHOICES),
        }


class AuditAdmin(admin.ModelAdmin):
    form = AuditAdminForm


DOCUMENT_VALIDATOR_CHOICES = (
    (k, k) for k in DocumentValidatorProvider.plugins.keys()
)


class DoctypeAdminForm(forms.ModelForm):
    class Meta:
        model = Doctype
        fields = '__all__'
        widgets = {
            'validator': forms.Select(choices=DOCUMENT_VALIDATOR_CHOICES),
        }


class DoctypeAdmin(admin.ModelAdmin):
    form = DoctypeAdminForm


admin.site.register(Audit, AuditAdmin)
admin.site.register(Doctype, DoctypeAdmin)
admin.site.register(Document)
admin.site.register(Package)
