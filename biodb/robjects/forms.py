from django import forms
from django.core.urlresolvers import reverse_lazy

from django_addanother.widgets import AddAnotherWidgetWrapper, AddAnotherEditSelectedWidgetWrapper

from .models import Robject


class RobjectForm(forms.ModelForm):
    class Meta:
        model = Robject
        fields = '__all__'
        widgets = {
            'name': AddAnotherWidgetWrapper(
                forms.Select,
                reverse_lazy('add_name', args=['test1']),
            ),
        }
