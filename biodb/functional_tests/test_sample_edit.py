from functional_tests.base import FunctionalTest
import time
from robjects.models import Robject
from samples.models import Sample
from samples import forms as sample_forms
from django.contrib.auth.models import User


class SampleEditTestCase(FunctionalTest):
    def test_annonymous_access(self):
        self.annonymous_testing_helper(self.SAMPLE_EDIT_URL)

    def test_access_without_view_permision(self):
        self.permission_view_testing_helper(self.SAMPLE_EDIT_URL)

    def test_url_kwargs_not_matching(self):
        self.not_matching_url_kwarg_helper(self.SAMPLE_EDIT_URL)

    def test_user_visits_robject_page(self):
        proj, user = self.default_set_up_for_modify_robjects_pages()
        robj = Robject.objects.create(project=proj)
        sample = Sample.objects.create(robject=robj)
        self.browser.get(self.SAMPLE_EDIT_URL)

        # iterate over field names in form, confirm id names
        for field_name in sample_forms.SampleForm.base_fields.keys():
            self.get_by_css(f"#id_{field_name}")

        # confirm pre-assigned status field
        status_field = self.get_by_css("#id_status option[value='1']")
        x = self.assertTrue(status_field.get_attribute("selected"))

        self.get_by_css("button.submit")

    def test_user_modify_all_fields(self):
        proj, sample_modificator = self.default_set_up_for_modify_robjects_pages()
        sample_creator = User.objects.create_user(
            username="CREATOR", password="CREATOR")
        robj = Robject.objects.create(project=proj)
        sample = Sample.objects.create(
            create_by=sample_creator,
            robject=robj,
            code="code",
            owner=sample_creator,
            notes="notes",
            form="form",
            source="source",
            status=Sample.UNASSIGNED
        )
        self.browser.get(self.SAMPLE_EDIT_URL)

        code_field = self.get_by_css("#id_code")
        owner_select_option = self.browser.find_element_by_xpath(
            "//select[@id='id_owner']/option[text()='USERNAME']")
        notes_field = self.get_by_css("#id_notes")
        form_field = self.get_by_css("#id_form")
        source_field = self.get_by_css("#id_source")
        status_select_option = self.browser.find_element_by_xpath(
            "//select[@id='id_status']/option[text()='Requested']")

        code_field.clear()
        code_field.send_keys("new_code")
        owner_select_option.click()
        notes_field.clear()
        notes_field.send_keys("new_notes")
        form_field.clear()
        form_field.send_keys("new_form")
        source_field.clear()
        source_field.send_keys("new_source")
        status_select_option.click()

        self.get_by_css(".submit").click()

        sample_modified = Sample.objects.last()

        self.assertEqual(sample_modified.code, "new_code")
        self.assertEqual(sample_modified.owner, sample_modificator)
        self.assertEqual(sample_modified.notes, "new_notes")
        self.assertEqual(sample_modified.form, "new_form")
        self.assertEqual(sample_modified.source, "new_source")
        self.assertEqual(sample_modified.status, Sample.REQUESTED)
        self.assertEqual(sample_modified.create_by, sample_creator)
        self.assertEqual(sample_modified.modify_by, sample_modificator)

    def test_user_submit_form_without_any_changes(self):
        proj, user = self.default_set_up_for_modify_robjects_pages()
        robj = Robject.objects.create(project=proj)
        sample = Sample.objects.create(robject=robj)

        self.browser.get(self.SAMPLE_EDIT_URL)

        self.get_by_css("button.submit").click()
        self.assertEqual(self.browser.current_url, self.SAMPLE_DETAILS_URL)
