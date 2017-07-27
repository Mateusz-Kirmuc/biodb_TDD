from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TestCase
from projects.models import Project
from projects.models import Robject
from django.contrib.auth.models import User


class ProjectModelTestCase(TestCase):

    def test_fields_classes(self):
        name_field = Project._meta.get_field("name")
        self.assertIsInstance(name_field, models.CharField)

    def test_proper_name_validation(self):
        proj = Project.objects.create(name="Top Secret")
        msg = "Name must be composed from letters, numbers or underscores."
        with self.assertRaises(ValidationError) as ex:
            proj.full_clean()
        self.assertIn("name", ex.exception.message_dict)
        self.assertIn(msg, ex.exception.message_dict["name"])

    def test_get_absolute_url(self):
        proj = Project.objects.create(name="top_secret")
        self.assertEqual(proj.get_absolute_url(),
                         "/projects/top_secret/robjects/")

    def test_project_name_uniqueness(self):
        Project.objects.create(name="PROJECT_1")
        with self.assertRaises(IntegrityError):
            Project.objects.create(name="PROJECT_1")


class RobjectModelTestCase(TestCase):
    def test_fields_classes(self):
        project_field = Robject._meta.get_field("project")
        self.assertIsInstance(project_field, models.ForeignKey)

        author_field = Robject._meta.get_field("author")
        self.assertIsInstance(author_field, models.ForeignKey)

        name_field = Robject._meta.get_field("name")
        self.assertIsInstance(name_field, models.CharField)

        create_by_field = Robject._meta.get_field("create_by")
        self.assertIsInstance(create_by_field, models.ForeignKey)

        create_date_field = Robject._meta.get_field("create_date")
        self.assertIsInstance(create_date_field, models.DateTimeField)

        modify_by_field = Robject._meta.get_field("modify_by")
        self.assertIsInstance(modify_by_field, models.ForeignKey)

    def test_str_method(self):
        robj = Robject(id=101)
        self.assertEqual(robj.__str__(), "Robject 101")

    def test_not_string_based_fields_may_be_null(self):
        author_field = Robject._meta.get_field("author")
        project_field = Robject._meta.get_field("project")
        create_by_field = Robject._meta.get_field("create_by")
        create_date_field = Robject._meta.get_field("create_date")
        modify_by_field = Robject._meta.get_field("modify_by")
        self.assertTrue(author_field.null)
        self.assertTrue(project_field.null)
        self.assertTrue(create_by_field.null)
        self.assertTrue(create_date_field.null)
        self.assertTrue(modify_by_field.null)

    def test_related_models_in_foreign_keys(self):
        author_field = Robject._meta.get_field("author")
        project_field = Robject._meta.get_field("project")
        create_by_field = Robject._meta.get_field("create_by")
        modify_by_field = Robject._meta.get_field("modify_by")

        self.assertEqual(author_field.related_model, User)
        self.assertEqual(project_field.related_model, Project)
        self.assertEqual(create_by_field.related_model, User)
        self.assertEqual(modify_by_field.related_model, User)
