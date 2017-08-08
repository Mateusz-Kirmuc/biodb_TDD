from django.test import TestCase
from robjects.models import Robject
from django.contrib.auth.models import User
from projects.models import Project
from django.db import models
from ckeditor.fields import RichTextField



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

        tags_field = Robject._meta.get_field("tags")
        self.assertIsInstance(tags_field, models.ManyToManyField)

        notes_field = Robject._meta.get_field("notes")
        self.assertIsInstance(notes_field, models.RichTextField)

        ligand_field = Robject._meta.get_field("ligand")
        self.assertIsInstance(ligand_field, models.CharField)

        receptor_field = Robject._meta.get_field("receptor")
        self.assertIsInstance(receptor_field, models.CharField)

        ref_seq_field = Robject._meta.get_field("ref_seq")
        self.assertIsInstance(ref_seq_field, models.RichTextField)

        mod_seq_field = Robject._meta.get_field("mod_seq")
        self.assertIsInstance(mod_seq_field, models.RichTextField)

        description_field = Robject._meta.get_field("description")
        self.assertIsInstance(description_field, models.RichTextField)

        bibliography_field = Robject._meta.get_field("bibliography")
        self.assertIsInstance(bibliography_field, models.RichTextField)

        ref_commercial_field = Robject._meta.get_field("ref_commercial")
        self.assertIsInstance(ref_commercial_field, models.RichTextField)

        ref_clinical_field = Robject._meta.get_field("ref_clinical")
        self.assertIsInstance(ref_clinical_field, models.RichTextField)


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

    def test_related_name_attr_in_create_by_field(self):
        self.assertEqual(
            Robject._meta.get_field("create_by").related_query_name(),
            "robjects_created_by_user")
