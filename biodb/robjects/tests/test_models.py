from django.test import TestCase
from robjects.models import Robject
from django.contrib.auth.models import User
from projects.models import Project
from projects.models import Tag
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
        self.assertIsInstance(notes_field, RichTextField)

        ligand_field = Robject._meta.get_field("ligand")
        self.assertIsInstance(ligand_field, models.CharField)

        receptor_field = Robject._meta.get_field("receptor")
        self.assertIsInstance(receptor_field, models.CharField)

        ref_seq_field = Robject._meta.get_field("ref_seq")
        self.assertIsInstance(ref_seq_field, RichTextField)

        mod_seq_field = Robject._meta.get_field("mod_seq")
        self.assertIsInstance(mod_seq_field, RichTextField)

        description_field = Robject._meta.get_field("description")
        self.assertIsInstance(description_field, RichTextField)

        bibliography_field = Robject._meta.get_field("bibliography")
        self.assertIsInstance(bibliography_field, RichTextField)

        ref_commercial_field = Robject._meta.get_field("ref_commercial")
        self.assertIsInstance(ref_commercial_field, RichTextField)

        ref_clinical_field = Robject._meta.get_field("ref_clinical")
        self.assertIsInstance(ref_clinical_field, RichTextField)

        mod_seq_field = Robject._meta.get_field("mod_seq")
        self.assertIsInstance(mod_seq_field, RichTextField)

        description_field = Robject._meta.get_field("description")
        self.assertIsInstance(description_field, RichTextField)

        bibliography_field = Robject._meta.get_field("bibliography")
        self.assertIsInstance(bibliography_field, RichTextField)

        ref_commercial_field = Robject._meta.get_field("ref_commercial")
        self.assertIsInstance(ref_commercial_field, RichTextField)

        ref_clinical_field = Robject._meta.get_field("ref_clinical")
        self.assertIsInstance(ref_clinical_field, RichTextField)

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

    def test_get_detail_fields(self):
        fields = ["ligand", "receptor", "ref_seq", "mod_seq", "description",
                  "bibliography", "ref_commercial", "ref_clinical", "notes"]

        # get a list of verbose names for each field
        verbose_names = []
        for field in fields:
            robject_field = Robject._meta.get_field(field)
            verbose_names.append(robject_field.verbose_name)
        # get a list of detail fields from robject method
        robj = Robject(name="testr1")
        detail_fields = robj.get_detail_fields()
        detail_names = list(zip(*detail_fields))[0]
        detail_list = list(detail_names)
        # check equal
        self.assertCountEqual(verbose_names, detail_list)

    def test_get_general_fields(self):
        fields = ["id", "create_date", "create_by",
                  "modify_date", "modify_by", "author"]

        # get a list of verbose names for each field
        verbose_names = []
        for field in fields:
            robject_field = Robject._meta.get_field(field)
            verbose_names.append(robject_field.verbose_name)
        # get a list of genral fields from robject method
        robj = Robject(name="testr1")
        general_fields = robj.get_general_fields()
        general_names = list(zip(*general_fields))[0]
        general_list = list(general_names)
        # check equal
        self.assertCountEqual(verbose_names, general_list)

    def test_get_fields(self):
        proj_instance = Project.objects.create(name='proj1_instance')
        rob_instance = Robject.objects.create(
            name='random1_robject', project=proj_instance)
        tag_instance = Tag.objects.create(
            name='tag1_instance', project=proj_instance)
        # get a list of verbose names for each field
        my_fields = ["name", "project", "tags", "id", "create_date", "create_by",
                     "modify_date", "modify_by", "author",
                     "ligand", "receptor", "ref_seq", "mod_seq", "description",
                     "bibliography", "ref_commercial", "ref_clinical", "notes"
                     ]

        fields_verbose = []
        fields = Robject._meta.get_fields()
        # get list of verbose_names from fields
        for field in fields:
            fields_verbose.append(field.verbose_name)
        # get a list of genral fields from robject method

        method_fields = Robject.get_fields(rob_instance, my_fields)
        method_fields_names = list(zip(*method_fields))[0]
        # create list from set
        method_fields_names_list = list(method_fields_names)

        # check equal
        self.assertCountEqual(fields_verbose, method_fields_names_list)

    def test_get_absolute_url(self):
        proj = Project(name="project_101")
        robj = Robject(project=proj, id=101, name="robj")

        self.assertEqual(robj.get_absolute_url(),
                         "/projects/project_101/robjects/101/details")
