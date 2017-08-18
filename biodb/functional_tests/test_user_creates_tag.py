import time
from datetime import datetime
from django.contrib.auth.models import User
from django.test import tag
from functional_tests.base import FunctionalTest
from projects.models import Project
from projects.models import Tag
from robjects.models import Robject
from selenium.common.exceptions import NoSuchElementException


@tag('slow')
class UserVisitsCreateTagPage(FunctionalTest):
    def test_annonymous_user_visits_create_tag_page(self):
        # To visit any tag page, project object needed.
        Project.objects.create(name="PROJECT_1")
        # Anonymous user goes to tags/create page. He sees permission denied
        # message
        self.browser.get(self.live_server_url +
                         "/projects/PROJECT_1/tags/create/")
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(body.text, "403 Forbidden")

    def test_logged_user_checks_current_project_tags(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")

        # User checks if Name: for is present on page
        create_section = self.browser.find_element_by_class_name(
            "create_section")
        self.assertEqual(create_section.text, "Name:")


@tag('slow')
class UserCreatesTag(FunctionalTest):
    def test_user_creates_correct_tag_and_saves_it(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("qwerty")

        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        # Check if tag is in tags list view.
        content = self.browser.find_element_by_tag_name("ul")
        self.assertIn('qwerty', content.text)

    def test_user_creates_two_correct_tags_and_saves_them(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("qwerty")

        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        # User goes again to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")

        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("qwerty1")

        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()
        # Check if two tags are in tag list view.
        tag_container = self.browser.find_element_by_css_selector(".tag_list")
        tag_list = tag_container.find_elements_by_tag_name("li")
        self.assertEqual(len(tag_list), 2)

    def test_user_creates_two_tags_with_the_same_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("qwerty")

        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        # User goes again to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")

        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("qwerty")

        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()
        # Check if two tags are in tag list view.
        error_message = self.browser.find_element_by_css_selector('.errorlist')
        self.assertEqual('Tag with this Name already exists.',
                         error_message.text)

    def test_user_creates_empty_name_tag_and_wants_to_save_it(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")

        # User left empty form and wants to save it.
        button = self.browser.find_element_by_id("Save")
        button.click()

        # User is still on the same page, can't add empty name tag.
        url = self.browser.current_url
        self.assertEqual(url, self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")

    def test_user_creates_to_long_tag_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type to long tag name in form
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("more_than_20_characters_string")
        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        content = self.browser.find_element_by_tag_name("ul")
        self.assertNotEqual('more_than_20_characters_string', content.text)

    def test_user_creates_20_characters_tag_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type exactly 20 characters in  name form
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("12345678901234567890")
        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        content = self.browser.find_element_by_tag_name("ul")
        self.assertIn('12345678901234567890', content.text)

    def test_user_creates_incorrect_tag_name(self):

        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # User goes to tag create page
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/create/")
        # type tag name with blank spaces
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("wrong name")
        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        error_message = self.browser.find_element_by_css_selector(".errorlist")
        self.assertIn("Enter a valid", error_message.text)
