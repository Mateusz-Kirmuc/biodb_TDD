# from django.contrib.auth.models import User
import string
from django.core.exceptions import ValidationError
from django.db import models
# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def clean(self):
        """
        Extra cleaning of name chars in Forms.
        Any ValidationError raised by this method will be associated
        with the 'name' field;
        """
        allowed_name_chars = string.ascii_letters + string.digits + '_-'
        msg = "Name must be composed from letters, numbers or underscores."
        for char in self.name:
            if char not in allowed_name_chars:
                raise ValidationError({"name": msg})

    def get_absolute_url(self):
        return "/projects/%s/robjects/" % self.name
