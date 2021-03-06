from django.test import TestCase
from robjects.models import Robject
from django.contrib.auth.models import User
from projects.models import Project
from django.db import models
from robjects.models import Name, Tag
from ckeditor.fields import RichTextField
from django import db
import datetime
from django.utils import timezone


class RobjectModelTestCase(TestCase):
    def check_Robject_has_attr(self, attr_name):
        if not hasattr(Robject, attr_name):
            self.fail(f"Robject doesn't have '{attr_name}' attr.")

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

    def test_related_name_attr_in_create_by_field(self):
        self.assertEqual(
            Robject._meta.get_field("create_by").related_query_name(),
            "robjects_created_by_user")

    def test_Robject_has_tags_field(self):
        try:
            Robject._meta.get_field("tags")
        except models.FieldDoesNotExist:
            self.fail("Robject doesn't have 'tags' field.")

    def test_Robject_has_names_field(self):
        try:
            Robject._meta.get_field("names")
        except models.FieldDoesNotExist:
            self.fail("Robject doesn't have 'names' field.")

    def test_project_field_is_not_blank(self):
        field = Robject._meta.get_field("project")
        self.assertTrue(field.blank)

    def test_create_by_field_is_not_blank(self):
        field = Robject._meta.get_field("create_by")
        self.assertTrue(field.blank)

    def test_create_date_field_is_blank(self):
        field = Robject._meta.get_field("create_date")
        self.assertTrue(field.blank)

    def test_modify_by_field_is_blank(self):
        field = Robject._meta.get_field("modify_by")
        self.assertTrue(field.blank)

    def test_way_to_get_robjects_related_to_given_tag(self):
        t = Tag.objects.create(name="tag")
        r1 = Robject.objects.create(name="robj_1")
        r1.tags.add(t)
        r2 = Robject.objects.create(name="robj_2")
        r2.tags.add(t)
        robjects = t.robjects.all()
        self.assertEqual(list(robjects), [r1, r2])

    def test_way_to_get_robjects_related_to_given_name(self):
        n = Name.objects.create(name="name")
        r1 = Robject.objects.create(name="robj_1")
        r1.names.add(n)
        r2 = Robject.objects.create(name="robj_2")
        r2.names.add(n)
        robjects = n.robjects.all()
        self.assertEqual(list(robjects), [r1, r2])

    def test_Robject_has_notes_attr(self):
        self.check_Robject_has_attr("notes")

    def test_Robject_has_ref_seq_attr(self):
        self.check_Robject_has_attr("ref_seq")

    def test_Robject_has_mod_seq_attr(self):
        self.check_Robject_has_attr("mod_seq")

    def test_Robject_has_description_attr(self):
        self.check_Robject_has_attr("description")

    def test_Robject_has_bibliography_attr(self):
        self.check_Robject_has_attr("bibliography")

    def test_Robject_has_ref_commercial_attr(self):
        self.check_Robject_has_attr("ref_commercial")

    def test_Robject_has_ref_clinical_attr(self):
        self.check_Robject_has_attr("ref_clinical")

    def test_Robject_has_ligand_attr(self):
        self.check_Robject_has_attr("ligand")

    def test_Robject_has_receptor_attr(self):
        self.check_Robject_has_attr("receptor")

    def test_ref_seq_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("ref_seq")
        self.assertIsInstance(field, RichTextField)

    def test_mod_seq_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("mod_seq")
        self.assertIsInstance(field, RichTextField)

    def test_ref_commercial_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("ref_commercial")
        self.assertIsInstance(field, RichTextField)

    def test_ref_clinical_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("ref_clinical")
        self.assertIsInstance(field, RichTextField)

    def test_ligand_field_is_CharField_instance_with_max_width_100(self):
        field = Robject._meta.get_field("ligand")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 100)

    def test_receptor_field_is_CharField_instance_with_max_width_100(self):
        field = Robject._meta.get_field("receptor")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 100)

    def test_notes_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("notes")
        self.assertIsInstance(field, RichTextField)

    def test_bibliography_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("bibliography")
        self.assertIsInstance(field, RichTextField)

    def test_description_field_is_RichTextField_instance(self):
        field = Robject._meta.get_field("description")
        self.assertIsInstance(field, RichTextField)

    def test_notes_field_is_blank(self):
        field = Robject._meta.get_field("notes")
        self.assertTrue(field.blank)

    def test_bibliography_field_is_blank(self):
        field = Robject._meta.get_field("bibliography")
        self.assertTrue(field.blank)

    def test_description_field_is_blank(self):
        field = Robject._meta.get_field("description")
        self.assertTrue(field.blank)

    def test_author_field_is_blank(self):
        field = Robject._meta.get_field("author")
        self.assertTrue(field.blank)

    def test_tags_field_is_blank(self):
        field = Robject._meta.get_field("tags")
        self.assertTrue(field.blank)

    def test_ref_seq_field_is_blank(self):
        field = Robject._meta.get_field("ref_seq")
        self.assertTrue(field.blank)

    def test_mod_seq_field_is_blank(self):
        field = Robject._meta.get_field("mod_seq")
        self.assertTrue(field.blank)

    def test_ref_commercial_field_is_blank(self):
        field = Robject._meta.get_field("ref_commercial")
        self.assertTrue(field.blank)

    def test_ref_clinical_field_is_blank(self):
        field = Robject._meta.get_field("ref_clinical")
        self.assertTrue(field.blank)

    def test_ligand_field_is_blank(self):
        field = Robject._meta.get_field("ligand")
        self.assertTrue(field.blank)

    def test_receptor_field_is_blank(self):
        field = Robject._meta.get_field("receptor")
        self.assertTrue(field.blank)

    def test_names_field_is_blank(self):
        field = Robject._meta.get_field("names")
        self.assertTrue(field.blank)

    def test_Robject_name_is_uniqe_within_project_only(self):
        from django.db import transaction
        proj_1 = Project.objects.create(name="proj_1")
        proj_2 = Project.objects.create(name="proj_2")
        Robject.objects.create(project=proj_1, name="taken_name")
        with self.assertRaises(db.IntegrityError):
            with transaction.atomic():
                Robject.objects.create(project=proj_1, name="taken_name")
        Robject.objects.create(project=proj_2, name="taken_name")

    def test_empty_Robject_name_is_null(self):
        r = Robject.objects.create()
        self.assertEqual(r.name, None)

    def test_create_date_field_is_assigned_automatically_to_creation_time(self):
        # NOTE: this test may crash becouse it depends on time execution which
        # may vary
        # Consider this solution: https://bytes.vokal.io/almost-equal/
        t = timezone.now()
        r = Robject.objects.create()
        self.assertAlmostEqual(r.create_date, t,
                               delta=datetime.timedelta(milliseconds=1))

    def test_modify_date_is_assigned_automatically_when_robject_is_saved(self):
        # NOTE: this test may crash becouse it depends on time execution which
        # may vary
        # Consider this solution: https://bytes.vokal.io/almost-equal/
        t1 = timezone.now()
        r = Robject.objects.create()
        self.assertAlmostEqual(r.modify_date, t1,
                               delta=datetime.timedelta(milliseconds=1))

        t2 = timezone.now()
        r.save()
        self.assertAlmostEqual(r.modify_date, t2,
                               delta=datetime.timedelta(milliseconds=1))

    def test_method_get_fields_names(self):
        # +++ test default behavior +++
        # this method should return list of robject names.
        # by defalut without relation fields
        expected_fields = set(f.name for f in Robject._meta.get_fields()
                              if not (f.is_relation or f.one_to_one or
                                      (f.many_to_one and f.related_model)))
        # create an instance
        robject = Robject.objects.create()
        fields_names = robject.get_fields_names()
        self.assertEqual(expected_fields, fields_names)
        # +++ test option relation to add relation fields names to list +++
        # create list of fields names including relational fields names
        expected_fields = set(f.name for f in Robject._meta.get_fields())
        fields_names_all = robject.get_fields_names(relation=True)
        self.assertEqual(expected_fields, fields_names_all)
        # +++ test option for fields excluding +++
        excluded_fields = ["name", "author", "names"]
        # fields should be in normal function call
        for efield in excluded_fields:
            self.assertIn(efield, fields_names_all)
        # call function with exclude options
        fields = robject.get_fields_names(exclude=excluded_fields)
        # fields are not allowed if function is called with
        for efield in excluded_fields:
            self.assertNotIn(efield, fields)


class NameModelTestCase(TestCase):
    def test_Name_has_name_field(self):
        try:
            Name._meta.get_field("name")
        except models.FieldDoesNotExist:
            self.fail("Name doesn't have 'name' field.")

    def test_name_field_is_char_field(self):
        self.assertIsInstance(Name._meta.get_field("name"), models.CharField)

    def test_str_method(self):
        n = Name.objects.create(name="hello")
        self.assertEqual(n.__str__(), "hello")

    def test_name_field_is_uniqe(self):
        Name.objects.create(name="taken")
        with self.assertRaises(db.IntegrityError):
            Name.objects.create(name="taken")


class TagModelTestCase(TestCase):
    def test_Tag_has_name_field(self):
        try:
            Tag._meta.get_field("name")
        except models.FieldDoesNotExist:
            self.fail("Tag doesn't have 'name' field.")

    def test_tag_field_is_char_field(self):
        self.assertIsInstance(Tag._meta.get_field("name"), models.CharField)

    def test_str_method(self):
        t = Tag.objects.create(name="bye")
        self.assertEqual(t.__str__(), "bye")

    def test_Tag_has_project_field(self):
        try:
            Tag._meta.get_field("project")
        except models.FieldDoesNotExist:
            self.fail("Tag doesn't have 'name' field.")

    def test_project_field_is_blank(self):
        field = Robject._meta.get_field("project")
        self.assertTrue(field.blank)

    def test_name_field_is_uniqe(self):
        Tag.objects.create(name="taken")
        with self.assertRaises(db.IntegrityError):
            Tag.objects.create(name="taken")

    def test_project_field_may_be_null(self):
        t = Tag.objects.create()
        self.assertEqual(t.project, None)
