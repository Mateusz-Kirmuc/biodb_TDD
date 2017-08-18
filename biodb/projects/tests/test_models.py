from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TestCase
from projects.models import Project
from projects.models import Tag


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


class TagModelTestCase(TestCase):

    def test_tag_name_uniqueness(self):
        proj = Project.objects.create(name="PROJECT_1")
        Tag.objects.create(name="Tag1", project=proj)
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Tag1", project=proj)

    def test_get_absolute_url(self):
        proj = Project.objects.create(name="top_secret")
        tag = Tag.objects.create(name="Tag1", project=proj)
        self.assertEqual(tag.get_absolute_url(),
                         f"/projects/top_secret/tags/")

    def test_tag_str(self):
        proj = Project.objects.create(name="top_secret")
        tag = Tag.objects.create(name="Tag1", project=proj)
        self.assertEqual(tag.__str__(), "Tag1")

    def test_tag_unicode(self):
        proj = Project.objects.create(name="top_secret")
        tag = Tag.objects.create(name="Tag1", project=proj)
        self.assertEqual(tag.__unicode__(), "Tag1")
