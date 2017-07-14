from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)

    def clean(self):
        allowed_name_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy\
                                                                   z0123456789_"
        msg = "Name must be composed from letters, numbers or underscores."
        for char in self.name:
            if char not in allowed:
                raise ValidationError({"name":msg})