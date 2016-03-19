from django import forms


CHOICES = (
    # Those should map with audits.Audit.runner_choices for all the
    # "dump-to-excel" runners. First items must match the runner class names.
    ('SefipToExcel', 'GFIP (arquivo .SFP)'),
    ('EfdDump', 'EFD Contribuições'),
    ('EcfDump', 'ECF'),
)


class OptInForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'id_name',
            'placeholder': 'Seu nome'
        }))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'id_email',
            'placeholder': 'Email'
        }))
    audit = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'id': 'id_audit'}),
        choices=CHOICES)
    document = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'id': 'id_file'}))

    def save(self):
        #TODO
        pass
