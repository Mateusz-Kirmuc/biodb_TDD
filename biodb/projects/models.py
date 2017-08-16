from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.text import slugify
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


class Tag(models.Model):
    """
        Model for keywords assigned to a Robject
        Require: name unique for a project.
    """
    name = models.SlugField(max_length=20, unique=True)
    project = models.ForeignKey(to=Project)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def clean(self):
        self.name = slugify(self.name)

    def get_absolute_url(self):
        return "/projects/%s/tags/" % (self.project.name)
