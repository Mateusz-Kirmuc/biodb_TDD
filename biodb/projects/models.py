import string
from django.core.exceptions import ValidationError
from django.db import models
from django.core.urlresolvers import reverse
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
        return reverse("projects:robjects:robjects_list", kwargs={"project_name": self.name})

    class Meta:
        permissions = (
            ("can_visit_project", "User can see project elements."),
            ("can_modify_project", "User can modify project elements."),
        )

    def __str__(self):
        return self.name


class RelatedModelsCustomQuerysetClass(models.QuerySet):
    """ Class which extends models.QuerySet and provides all_as_string method
    """
    def all_as_string(queryset):
        """ Method joins objects from queryset into comma separated string
        """
        all_as_list_of_strings = [obj.__str__() for obj in queryset]
        _all_as_string = ", ".join(all_as_list_of_strings)
        return _all_as_string


class RelatedModelsCustomManager(models.Manager):
    """ Custom manager for related models (like Tag, Name)
    """

    def get_queryset(self):
        """ Method specifies CQC as a default QS class to use inside models
        """
        return RelatedModelsCustomQuerysetClass(self.model, using=self._db)
