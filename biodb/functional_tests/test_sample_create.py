from functional_tests.base import FunctionalTest
import time
from django.contrib.auth.models import User


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
        code_input = self.browser.find_element_by_tag_name("input")
        self.assertEqual(code_input.get_attribute("placeholder"), "code")

        owner_input = self.browser.find_element_by_tag_name("select")
        owner_option = owner_input.find_element_by_css_selector(
            "option[selected]")
        self.assertEqual(owner_option.text, "logged_user")

        notes_input = self.browser.find_element_by_tag_name("textarea")
        self.assertEqual(notes_input.get_attribute("placeholder"), "notes")

        # Content user logs out.
        self.fail("Finish test!")
