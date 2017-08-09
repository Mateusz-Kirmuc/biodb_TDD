from projects.models import Project
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
#from simple_history.models import HistoricalRecords
from django.forms.models import model_to_dict


class Tag(models.Model):
    """
        Model for keywords assigned to a Robject
        Require: name unique for a project.
    """
    name = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Robject(models.Model):
    """
        Research Object containig data about research structures like protein or ligands or both (conjugates)
    """
    project = models.ForeignKey(to=Project, null=True)
    author = models.ForeignKey(
        to=User, null=True, related_name="robjects_in_which_user_is_author")
    name = models.CharField(max_length=100)
    create_by = models.ForeignKey(
        to=User, related_name="robjects_created_by_user", null=True)
    create_date = models.DateTimeField (null=True, auto_now_add=True )
    modify_date = models.DateTimeField(null=True, auto_now=)
    modify_by = models.ForeignKey(to=User, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    notes = RichTextField(null=True, blank=True)
    ligand = models.CharField(max_length=100, blank=True, null=True)
    receptor = models.CharField(max_length=100, blank=True, null=True)
    ref_seq = RichTextField(blank=True, null=True)
    mod_seq = RichTextField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    bibliography = RichTextField(blank=True, null=True)
    ref_commercial = RichTextField(blank=True, null=True)
    ref_clinical = RichTextField(blank=True, null=True)

    def __str__(self):
        return "Robject " + str(self.id)

    def get_absolute_url(self):
        return "/projects/%s/robjects/%s/details" % (self.project.name, self.id)

    @staticmethod
    def get_fields(instance, fields=[]):
        """
        Return dictionary with object fields: {field.verbose_name: field class, ...}

        Attrs:
        """
        fields_dict = {field.verbose_name: getattr(
            instance, field.name) for field in instance._meta.fields if field.name in fields}
        return sorted(fields_dict.items())

    def get_general_fields(self):
        '''
            Return fields : id, create_date, create_by, modify_date, modify_by, author
        '''
        fields = ["id", "create_date", "create_by",
                  "modify_date", "modify_by", "author"]
        return self.get_fields(self, fields)

    def get_detail_fields(self):
        '''
            Return fields: ligand. receptor. ref_seq, mod_seq, description, bibliography, ref_commercial, ref_clinical, notes
        '''
        fields = ["ligand", "receptor", "ref_seq", "mod_seq", "description",
                  "bibliography", "ref_commercial", "ref_clinical", "notes"]
        return self.get_fields(self, fields)
