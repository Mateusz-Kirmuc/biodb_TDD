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
from selenium.common.exceptions import NoSuchElementException
from django.test import override_settings


class SampleCreateTestCase(FunctionalTest):
    def find_tag(self, *args, **kwargs):
        return self.browser.find_element_by_tag_name(*args, **kwargs)

    def find_tags(self, *args, **kwargs):
        return self.browser.find_elements_by_tag_name(*args, **kwargs)

    @tag("ft_sample_create_1")
    def test_user_visit_page(self):
        # Admin register new user.
        # User heard about new feature in biodb app: sample creation form!
        # He knows that he can get there through robject detail page.
        user = self.help_register_new_user_and_get_sample_create(
            "USERNAME", "PASSWORD")

        # User decides to slightly look around.
        # He sees several input elements.
        code_input = self.find_tags("input")[0]
        self.assertEqual(code_input.get_attribute("placeholder"), "code")

        owner_input = self.find_tags("select")[0]
        owner_options = owner_input.find_elements_by_tag_name("option")
        self.assertEqual(len(owner_options), 1)
        owner_option = owner_input.find_element_by_css_selector(
            "option[selected]")
        self.assertEqual(owner_option.text, user.username)

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

        # Content user logs out.
        self.logout()

    @tag("ft_sample_create_2")
    def test_user_creates_full_sample(self):
        # Admin register new user.
        # User wants to test new feature in biodb app.
        # He goes to form page.
        user = self.help_register_new_user_and_get_sample_create(
            "USERNAME", "PASSWORD")

        # User fills all text inputs and set status as 'Production' status.
        self.help_enter_sample_code("test_code")
        self.find_by_css(
            "textarea[placeholder='notes']").send_keys("test_notes")
        self.find_by_css("input[placeholder='form']").send_keys("test_form")
        self.find_by_css("input[placeholder='source']").send_keys(
            "test_source")
        self.browser.find_element_by_xpath(
            "//option[contains(text(), 'Production')]").click()

        # Now user clicks submit button.
        self.help_submit_form()

        # GET LAST CREATED SAMPLE
        last_sample = Sample.objects.last()

        # He notice he was redirected to sample detail page.
        # In this page he wants to confirm all previous submitted data.
        self.help_confirm_sample_code("test_code")
        rest_sample_data_in_template = self.find_tags("li")
        self.assertEqual(
            rest_sample_data_in_template[0].text,
            f"Robject name : {self.robject.name}"
        )
        self.assertEqual(
            rest_sample_data_in_template[1].text, f"Owner : {user.username}")

        self.assertEqual(
            rest_sample_data_in_template[2].text,
            f"Create date : {last_sample.create_date.strftime(settings.DATETIME_FORMAT_TRANSLATED)}")

        self.assertEqual(
            rest_sample_data_in_template[3].text,
            f"Modify date : {last_sample.modify_date.strftime(settings.DATETIME_FORMAT_TRANSLATED)}"
        )

        self.assertEqual(
            rest_sample_data_in_template[4].text,
            f"Modify by : {user.username}"
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
        # Admin adds new user to biodb on demand.
        # First user logs in to Biodb and goes to sample create form.
        self.help_register_new_user_and_get_sample_create(
            username="user_1", password="password_1")

        # User sees that there is only one owner option.
        owner_input = self.find_tags("select")[0]
        self.assertEqual(
            len(owner_input.find_elements_by_tag_name("option")), 1)
        owner_option = owner_input.find_element_by_css_selector(
            "option[selected]")
        self.assertEqual(owner_option.text, "user_1")

        # User enters sample code and submit form.
        self.help_enter_sample_code("1234ABCD")
        self.help_submit_form()

        # Now he can see his sample in sample details page.
        self.help_confirm_sample_code("1234ABCD")

        # User 1 logs out.
        self.logout()

        # Here, admin register second user and let him know.
        # User goes to sample create form.
        self.help_register_new_user_and_get_sample_create(
            "user_2", "password_2")

        # User notice two usernames in template owner select element -- his name
        # and user_1's name.
        owner_options = self.browser.find_elements_by_css_selector(
            "select.owner option")
        self.assertEqual(len(owner_options), 2)
        self.assertIn("user_1", [option.text for option in owner_options])
        self.assertIn("user_2", [option.text for option in owner_options])

        # He picks his username.
        self.browser.find_element_by_xpath(
            "//option[contains(text(), 'user_2')]").click()
        # Then he pass sample code and submit form.
        self.help_enter_sample_code("xyz123")
        self.help_submit_form()

        # Now user_2 can see his sample in sample details page.
        self.help_confirm_sample_code("xyz123")
        self.assertEqual(self.find_by_css(".owner").text, "Owner : user_2")

        # User 2 logs out.
        self.logout()

    def test_user_submit_empty_form(self):
        # Admin register new user on demand.
        # New user goes to sample create form.
        self.help_register_new_user_and_get_sample_create(
            username="new_user", password="passwd")

        # STORE FORM PAGE URL.
        url = self.browser.current_url

        # He is very inquisitive and decide to submit empty form.
        self.help_submit_form()

        # It turns out user stays on the same page and sees information above
        # code input states that this field is required.
        self.assertEqual(self.browser.current_url, url)
        error_element = self.browser.find_element_by_xpath(
            "//input[@name='code']/preceding-sibling::p")
        self.assertEqual(error_element.text, "This field is required")

        # User corrects form and resubmits.
        self.help_enter_sample_code("sample_code")
        self.help_submit_form()

        # Now, he can confirm submitted data in sample details page.
        self.help_confirm_sample_code("sample_code")

        # Satisfied user logs out.

    def test_user_sees_error_message_only_when_submit_empty_form(self):
        # Admin register new user.
        # User wants to add new sample so he goes to sample create form.
        self.help_register_new_user_and_get_sample_create(
            "user_1", password="passwd_1")

        # He makes sure he doesn't see paragraph with error message above code
        # input.
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_xpath(
                "//input[@name='code']/preceding-sibling::p")

        # User decides to submit empty form.
        self.help_submit_form()

        # Now, he sees error message above code input.
        error_element = self.browser.find_element_by_xpath(
            "//input[@name='code']/preceding-sibling::p")
        self.assertEqual(error_element.text, "This field is required")

        # User logs out.

    def help_enter_sample_code(self, code):
        self.find_by_css("input[placeholder='code']").send_keys(code)

    def help_submit_form(self):
        self.find_tag("button").click()

    def help_register_new_user(self, username, password):
        user = User.objects.create_user(
            username=username, password=password)
        return user

    def help_confirm_sample_code(self, code):
        self.assertEqual(self.find_tag("h1").text, code)

    def help_register_new_user_and_get_sample_create(self, username, password):
        user = self.help_register_new_user(username, password)
        time.sleep(0.2)
        self.get_sample_create_page(user, password)
        return user

    def test_annonymous_user_tries_to_get_sample_create_form(self):
        # Admin register new user.
        self.help_register_new_user(username="user_1", password="passwd_1")
        # User tries to get sample create form using url but he forgets to log
        # in.
        # He heard about project named 'project_1' and research object with id=1
        # within 'project_1'.
        # User knows about sample create url and uses those data within url.
        sample_create_url = self.live_server_url + reverse("projects:robjects:sample_create",
                                                           kwargs={"project_name": "project_1", "robject_id": 1})
        self.browser.get(sample_create_url)

        # Instead expected form user encounters login form.
        self.assertEqual(self.find_tag("h1").text, "Welcome to BioDB")

        # He enters his creadentials and submit login form.
        inputs = self.browser.find_elements_by_tag_name("input")
        inputs[0].send_keys("user_1")
        inputs[1].send_keys("passwd_1")
        self.help_submit_form()

        # Now, he finally sees sample create form and its url.
        self.assertEqual(self.browser.current_url, sample_create_url)

    @override_settings(DEBUG=True)
    def test_user_without_project_visit_permission_tries_to_get_form(self):
        # Admin register new user on demand.
        user = User.objects.create_user(username="user_1", password="passwd_1")

        # New user logs in.
        self.login(user, "passwd_1")

        # His friend ask him to create new sample instead of him.
        # For this purpose friend has sent the user link to the page with this
        # form.
        # HERE DB NEEDS SOME SETUP
        project = Project.objects.create(name="project_1")
        robject = Robject.objects.create(project=project)
        link = reverse("projects:robjects:sample_create", kwargs={
            "project_name": project.name,
            "robject_id": robject.id
        })

        # User use this ling to get to sample create form.
        self.browser.get(self.live_server_url + link)

        # Unexpectedly, user encounets message stating that user does not have
        # required 'project visit message'.
        self.assertEqual(self.find_tag("h1").text,
                         "User doesn't have permission: can visit project")
        # Disappointed user logs out and sends message to admin what's going on.
        self.logout()
        # Admin assign required permission to user and lets him know about this
        # fact.
        assign_perm("can_visit_project", user, project)

        # Now, user logs in and goes to sample create form again.
        self.login(user, "passwd_1")
        self.browser.get(self.live_server_url + link)

        # He finally achieves his goal.
        self.find_by_css("input[placeholder='code']")

        # Now, user can safely logs out.
        self.logout()
