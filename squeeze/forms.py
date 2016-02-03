from django import forms

CHOICES = (('1', 'First'), ('2', 'Second'))




class OptInForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'id':'id_name','placeholder':'Seu nome'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'id':'id_email','placeholder':'Email'}))
    audit = forms.ChoiceField(widget=forms.RadioSelect(
        attrs={'id':'id_audit'}), choices=CHOICES)
    document = forms.FileField(widget=forms.ClearableFileInput(attrs={
        'id':'id_file'}))
