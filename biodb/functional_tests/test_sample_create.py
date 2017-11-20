from functional_tests.base import FunctionalTest
import time
from django.contrib.auth.models import User
from samples.models import Sample
from django.core.urlresolvers import reverse
from projects.models import Project
from django.test import tag
from robjects.models import Robject
from guardian.shortcuts import assign_perm
from biodb import settings


class SampleCreateTestCase(FunctionalTest):
    def find_tag(self, *args, **kwargs):
        return self.browser.find_element_by_tag_name(*args, **kwargs)

    def find_tags(self, *args, **kwargs):
        return self.browser.find_elements_by_tag_name(*args, **kwargs)

    @tag("ft_sample_create_1")
    def test_user_visit_page(self):
        # User heard about new feature in biodb app: sample creation form!
        # He knows that he can get there through robject detail page.
        self.get_sample_create_page()

        # User decides to slightly look around.
        # He sees several input elements.
        code_input = self.find_tags("input")[0]
        self.assertEqual(code_input.get_attribute("placeholder"), "code")

        owner_input = self.find_tags("select")[0]
        owner_options = owner_input.find_elements_by_tag_name("option")
        self.assertEqual(len(owner_options), 1)
        owner_option = owner_input.find_element_by_css_selector(
            "option[selected]")
        self.assertEqual(owner_option.text, self.user.username)

        notes_input = self.find_tag("textarea")
        self.assertEqual(notes_input.get_attribute("placeholder"), "notes")

        notes_input = self.find_tags("input")[1]
        self.assertEqual(notes_input.get_attribute("placeholder"), "form")

        notes_input = self.find_tags("input")[2]
        self.assertEqual(notes_input.get_attribute("placeholder"), "source")

        status_input = self.find_tags("select")[1]
        status_options = status_input.find_elements_by_tag_name("option")
        choices = [choice[1] for choice in Sample.STATUS_CHOICES]
        for idx, choice in enumerate(choices):
            self.assertEqual(choice, status_options[idx].text)

        button = self.find_tag("button")
        self.assertEqual(button.text, "Submit")

        # Content user logs out.

    @tag("ft_sample_create_2")
    def test_user_creates_full_sample(self):
        # User wants to test new feature in biodb app. He goes to form page.
        self.get_sample_create_page()

        # User fills all text inputs and set status as 'Production' status.
        self.find_by_css("input[placeholder='code']").send_keys("test_code")
        self.find_by_css(
            "textarea[placeholder='notes']").send_keys("test_notes")
        self.find_by_css("input[placeholder='form']").send_keys("test_form")
        self.find_by_css("input[placeholder='source']").send_keys(
            "test_source")
        self.browser.find_element_by_xpath(
            "//option[contains(text(), 'Production')]").click()

        # Now user clicks submit button.
        self.find_tag("button").click()

        # GET LAST CREATED SAMPLE
        last_sample = Sample.objects.last()

        # He notice he was redirected to sample detail page.
        # In this page he wants to confirm all previous submitted data.
        sample_code_in_template = self.find_tag("h1")
        self.assertEqual(sample_code_in_template.text, "test_code")
        rest_sample_data_in_template = self.find_tags("li")
        self.assertEqual(
            rest_sample_data_in_template[0].text,
            f"Robject name : {self.robject.name}"
        )
        self.assertEqual(
            rest_sample_data_in_template[1].text, f"Owner : {self.user.username}")

        self.assertEqual(
            rest_sample_data_in_template[2].text,
            f"Create date : {last_sample.create_date.strftime(settings.DATETIME_FORMAT_TRANSLATED)}")

        self.assertEqual(
            rest_sample_data_in_template[3].text,
            f"Modify date : {last_sample.modify_date.strftime(settings.DATETIME_FORMAT_TRANSLATED)}"
        )

        self.assertEqual(
            rest_sample_data_in_template[4].text,
            f"Modify by : {self.user.username}"
        )

        self.assertEqual(
            rest_sample_data_in_template[5].text,
            f"Notes : {last_sample.notes}"
        )

        self.assertEqual(
            rest_sample_data_in_template[6].text,
            f"Form :{last_sample.form}"
        )

        self.assertEqual(
            rest_sample_data_in_template[7].text,
            f"Source :{last_sample.source}"
        )

        self.assertEqual(
            rest_sample_data_in_template[8].text,
            f"Status : {Sample.STATUS_CHOICES[last_sample.status-1][1]}"
        )

        # When he finish, he logs out.

    def test_two_users_creates_samples(self):
        pass
        # First user logs in to Biodb.
        # He goes to sample create form and fills it.
        # Next, user confirms created sample in sample details page.
        # First user logs out.
        # Now, second user logs in.
        # He goes to the same form (within idenical project and robject) and
        # fills it.
        # Again, second user confirms created sample in sample details page.
        # Finally, second user logs out.
