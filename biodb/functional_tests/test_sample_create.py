from functional_tests.base import FunctionalTest
import time
from django.contrib.auth.models import User
from samples.models import Sample


class SampleCreateTestCase(FunctionalTest):
    def test_user_visit_page(self):
        # SET UP
        logged_user = User.objects.create_user(
            username="logged_user", password="logged_user_password")
        self.login_user(username="logged_user",
                        password="logged_user_password")
        # User heard about new feature in biodb app: sample creation form!
        # He goes to dedicated url.
        self.browser.get(self.live_server_url +
                         "/projects/project_1/samples/create/")
        # User decides to slightly look around.
        # He sees several input elements.
        code_input = self.browser.find_elements_by_tag_name("input")[0]
        self.assertEqual(code_input.get_attribute("placeholder"), "code")

        owner_input = self.browser.find_elements_by_tag_name("select")[0]
        owner_option = owner_input.find_element_by_css_selector(
            "option[selected]")
        self.assertEqual(owner_option.text, "logged_user")

        notes_input = self.browser.find_element_by_tag_name("textarea")
        self.assertEqual(notes_input.get_attribute("placeholder"), "notes")

        notes_input = self.browser.find_elements_by_tag_name("input")[1]
        self.assertEqual(notes_input.get_attribute("placeholder"), "form")

        notes_input = self.browser.find_elements_by_tag_name("input")[2]
        self.assertEqual(notes_input.get_attribute("placeholder"), "source")

        status_input = self.browser.find_elements_by_tag_name("select")[1]
        status_options = status_input.find_elements_by_tag_name("option")
        choices = [choice[1] for choice in Sample.STATUS_CHOICES]
        for choice in choices:
            self.assertIn(choice, [option.text for option in status_options])

        # Content user logs out.
        self.fail("Finish test!")
