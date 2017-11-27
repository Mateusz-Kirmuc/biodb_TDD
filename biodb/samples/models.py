from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from robjects.models import Robject
# Create your models here.


class Sample(models.Model):
    """
        Robjects sample object.
    """
    UNASSIGNED = 1
    REQUESTED = 2
    MOL_MOD = 3
    # IN_PROGRESS
    PREP = 5
    OPTIMAILIZATION = 6
    PRODUCTION = 7
    QA_CONTROL = 8
    COMPLETED = 9
    CANCELED = 10
    ON_HOLD = 11
    LIBRARY = 12

    STATUS_CHOICES = ((UNASSIGNED, 'Unassigned'),
                      (REQUESTED, 'Requested'),
                      (MOL_MOD, 'Molecular Modelling'),
                      (PREP, 'Preperation'),
                      (OPTIMAILIZATION, 'Optimalization'),
                      (PRODUCTION, 'Production'),
                      (QA_CONTROL, 'Quality Control'),
                      (COMPLETED, 'Completed'),
                      (CANCELED, 'Canceled'),
                      (ON_HOLD, 'ON_HOLD'),
                      (LIBRARY, 'Library'))

    code = models.CharField(max_length=100, blank=True)
    robject = models.ForeignKey(to=Robject, null=True)
    owner = models.ForeignKey(
        to=User, null=True, related_name="sample_in_which_user_is_owner")
    create_date = models.DateTimeField(null=True, auto_now_add=True)
    modify_date = models.DateTimeField(null=True, auto_now=True)
    modify_by = models.ForeignKey(to=User, null=True)
    notes = RichTextField(blank=True)
    form = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    def __str__(self):
        return "Sample " + str(self.id)

    @staticmethod
    def get_fields(instance, fields=None):
        """
        Return dictionary with object fields:
            {field.verbose_name: field class, ...}

        Attrs:
        """
        if not fields:
            fields = []
        fields_dict = {field.verbose_name: getattr(
            instance, field.name) for field in instance._meta.get_fields()
            if field.name in fields}
        return sorted(fields_dict.items())
