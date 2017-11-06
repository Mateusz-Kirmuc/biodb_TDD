from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TestCase
from projects.models import Project
from robjects.models import Tag
from django.core.urlresolvers import reverse


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
                         reverse("projects:robjects:robjects_list",
                                 kwargs={"project_name": proj.name}))

    def test_project_name_uniqueness(self):
        Project.objects.create(name="PROJECT_1")
        with self.assertRaises(IntegrityError):
            Project.objects.create(name="PROJECT_1")

    def test_Project_has_view_permission(self):
        self.assertIn(
            ("can_visit_project", "User can see project elements."),
            Project._meta.permissions)

    def test_Project_has_modify_permission(self):
        self.assertIn(
            ("can_modify_project", "User can modify project elements."),
            Project._meta.permissions)


class TagModelTestCase(TestCase):
    def test_fields_classes(self):
        name_field = Tag._meta.get_field("name")
        self.assertIsInstance(name_field, models.CharField)

        # project_field = Tag._meta.get_field("project")
        # self.assertIsInstance(project_field, models.ForeignKey)

    # def test_Tag_related_to_project(self):
    #     is_related = hasattr(Tag, "project")
    #     self.assertEqual(is_related, "True")

    def test_relation_between_Tag_and_Project(self):
        p = Project.objects.create(name="test_proj")
        t1 = Tag.objects.create(name="test_tag_1", project=p)
        t2 = Tag.objects.create(name="test_tag_2", project=p)
        self.assertListEqual(list(p.tags.all()), [t1, t2])
        self.assertEqual(t1.project, p)
        self.assertEqual(t2.project, p)

    def test_absolute_url(self):
        p = Project.objects.create(name="test_proj")
        t1 = Tag.objects.create(name="test_tag_1", project=p)
        self.assertEqual(t1.get_absolute_url(), "/projects/test_proj/tags/")
