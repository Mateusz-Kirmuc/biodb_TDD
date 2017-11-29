from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from samples.models import Sample
from robjects.models import Robject
from projects.models import Project
from django.db.utils import IntegrityError


class SampleModelTestCase(TestCase):
    def test_fields_classes(self):
        code_field = Sample._meta.get_field("code")
        self.assertIsInstance(code_field, models.CharField)

        robject_field = Sample._meta.get_field("robject")
        self.assertIsInstance(robject_field, models.ForeignKey)

        owner_field = Sample._meta.get_field("owner")
        self.assertIsInstance(owner_field, models.ForeignKey)

        create_date_field = Sample._meta.get_field("create_date")
        self.assertIsInstance(create_date_field, models.DateTimeField)

        modify_date_field = Sample._meta.get_field("modify_date")
        self.assertIsInstance(modify_date_field, models.DateTimeField)

        modify_by_field = Sample._meta.get_field("modify_by")
        self.assertIsInstance(modify_by_field, models.ForeignKey)

        notes_field = Sample._meta.get_field("notes")
        self.assertIsInstance(notes_field, RichTextField)

        form_field = Sample._meta.get_field("form")
        self.assertIsInstance(form_field, models.CharField)

        source_field = Sample._meta.get_field("source")
        self.assertIsInstance(source_field, models.CharField)

        status_field = Sample._meta.get_field("status")
        self.assertIsInstance(status_field, models.IntegerField)

    def test_not_string_based_fields_may_be_null(self):
        owner_field = Sample._meta.get_field("owner")
        robject_field = Sample._meta.get_field("robject")
        create_date_field = Sample._meta.get_field("create_date")
        modify_by_field = Sample._meta.get_field("modify_by")

        self.assertTrue(owner_field.null)
        self.assertTrue(robject_field.null)
        self.assertTrue(create_date_field.null)
        self.assertTrue(modify_by_field.null)

    def test_related_models_in_foreign_keys(self):
        owner_field = Sample._meta.get_field("owner")
        project_field = Sample._meta.get_field("robject")
        modify_by_field = Sample._meta.get_field("modify_by")

        self.assertEqual(owner_field.related_model, User)
        self.assertEqual(project_field.related_model, Robject)
        self.assertEqual(modify_by_field.related_model, User)

    def test_get_fields(self):
        proj_instance = Project.objects.create(name='proj1_instance')
        rob_instance = Robject.objects.create(
            name='random1_robject', project=proj_instance)
        sample_instance = Sample.objects.create(
            code='sample1_instance', robject=rob_instance)
        # get a list of verbose names for each field
        my_fields = ['robject', 'code', 'owner', 'create_date',
                     'modify_date', 'modify_by', 'notes', 'id',
                     'form', 'source', 'status'
                     ]

        fields_verbose = []
        fields = Sample._meta.get_fields()
        # get list of verbose_names from fields
        for field in fields:
            fields_verbose.append(field.verbose_name)
        # get a list of genral fields from robject method

        method_fields = Sample.get_fields(sample_instance, my_fields)
        method_fields_names = list(zip(*method_fields))[0]
        # create list from set
        method_fields_names_list = list(method_fields_names)

        # check equal
        self.assertCountEqual(fields_verbose, method_fields_names_list)

    def test_sample_code_must_be_uniqe(self):
        Sample.objects.create(code="xyz123")
        with self.assertRaises(IntegrityError):
            Sample.objects.create(code="xyz123")
