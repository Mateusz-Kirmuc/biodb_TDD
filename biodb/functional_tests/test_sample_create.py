from functional_tests.base import FunctionalTest
import time


class SampleCreateTestCase(FunctionalTest):
    def test_user_visit_page(self):
        # User heard about new feature in biodb app: sample creation form!
        # He goes to dedicated url.
        self.browser.get(self.live_server_url +
                         "/projects/project_1/samples/create/")
        # User decides to slightly look around.
        # He sees several input elements.
        code_input = self.browser.find_element_by_tag_name("input")
        self.assertEqual(code_input.get_attribute("placeholder"), "code")
        # Content user logs out.
        self.fail("Finish test!")
