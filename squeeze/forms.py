from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from audits.models import Audit, Doctype, Document
from jobs.models import Job
from squeeze.models import SqueezeJob, random_key


def get_beta_user():
    User = get_user_model()
    beta_user, created = User.objects.get_or_create(
        email='beta@paranoidlabs.com.br',
        defaults={
            'password': random_key(),
        })

    return beta_user


CHOICES = (
    # Those should map with audits.Audit.runner_choices for all the
    # "dump-to-excel" runners. First items must match the runner class names.
    ('SefipToExcel', 'GFIP (extensão .SFP)'),
    ('EfdDump', 'EFD Contribuições (extensão .sped)'),
    ('EcfDump', 'ECF (extensão .sped)'),
)


class OptInForm(forms.Form):
    name = forms.CharField(
        label='Seu nome',
        widget=forms.TextInput(attrs={
            'id': 'id_name',
        }))
    email = forms.EmailField(
        label='Seu email',
        widget=forms.EmailInput(attrs={
            'id': 'id_email',
        }))
    audit = forms.ChoiceField(
        widget=forms.Select(attrs={'id': 'id_audit'}),
        choices=CHOICES)
    document = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'id': 'id_document'}))


    def save(self):
        if not self.is_valid():
            raise ValidationError("Can't save a form with invalid data.")

        # Get audit.Audit instance
        audit = Audit.objects.get(runner=self.data['audit'])
        document = Document.objects.create(
            doctype = audit.required_doctypes.first(),
            file = self.files['document'],
            user = get_beta_user(),
        )

        # Instantiate jobs.Job and pass document id to it
        job = Job.objects.create(audit=audit, user=get_beta_user())
        job.documents.add(document.pk)

        # Instantiate squeeze.SqueezeJob
        squeezejob = SqueezeJob.objects.create(
            job = job,
            real_user_email=self.data['email'],
            real_user_name=self.data['name'],

        )

        return squeezejob
