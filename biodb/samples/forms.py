from django import forms
from samples.models import Sample


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        exclude = ("create_by", "modify_by", "robject")
