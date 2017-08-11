# from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def clean(self):
        allowed_name_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy\
z0123456789_"
        msg = "Name must be composed from letters, numbers or underscores."
        for char in self.name:
            if char not in allowed_name_chars:
                raise ValidationError({"name": msg})

    def get_absolute_url(self):
        return "/projects/%s/robjects/" % self.name
