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
    def test_user_visits_update_tag_page(self):
        # To visit any tag page, project object needed.
        usr1, proj1 = self.project_set_up_using_default_data()
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # Logged user goes to tags/edit page. He sees input_form Name:
        url = self.browser.get(self.live_server_url +
                               f"/projects/PROJECT_1/tags/{tag1.id}/edit/")

        body = self.browser.find_element_by_tag_name("body")
        self.assertIn('Name', body.text)

    def test_annonymous_user_visits_update_tag_page(self):
        # To visit any tag page, project object needed.
        proj1 = Project.objects.create(name="PROJECT_1")
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # Anonymous user goes to tags/create page. He sees permission denied
        # message
        self.browser.get(self.live_server_url +
                         f"/projects/PROJECT_1/tags/{tag1.id}/edit/")
        # New in Django 1.11, decorator method instead of LoginRequiredMixin
        # Returns permited page for annonymous user not '403 Forbiden'
        body = self.browser.find_element_by_tag_name("h1")
        # Useer is redirected to home biodb page
        self.assertEqual(body.text, "Welcome to BioDB")


@tag('slow')
class UserCreatesTag(FunctionalTest):
    def test_user_edit_to_correct_tag_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")
        # Create sample tag
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        input_form.send_keys("updated_tag_name")

        # user clicks Update button
        button = self.browser.find_element_by_id("Update")
        button.click()

        # User is redirected to tags list page
        # Check if tag is in tags list view.
        content = self.browser.find_element_by_tag_name("ul")
        self.assertIn('updated_tag_name', content.text)

    def test_user_updates_tag_to_repeated_tag_name(self):

        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample tag
        tag1 = Tag.objects.create(name='tag1_name', project=proj1)
        # Create other Tag to the same project tag
        tag2 = Tag.objects.create(name='tag2_name', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag2.id}/edit/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        # Rename tag to already existed name send.keys doesn't see capital letters
        # if the name of tag is Upercase it is possible to add same tag name lowercase
        input_form.send_keys("tag1_name")
        # user clicks Update button
        button = self.browser.find_element_by_id("Update")
        button.click()

        # User is redirected to tags list page
        # Check if tag is in tags list view.
        print (self.browser.find_element_by_tag_name('body').text)
        error_message = self.browser.find_element_by_css_selector('.errorlist')
        self.assertEqual('Tag with this Name already exists.',
                         error_message.text)

    def test_user_updates_two_correct_tags_and_saves_them(self):

        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")
        # Create sample tag
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        # Create other Tag to the same project tag
        tag2 = Tag.objects.create(name='Tag2', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        input_form.send_keys("updated_tag1_name")
        button = self.browser.find_element_by_id("Update")
        button.click()
        # User goes to other create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag2.id}/edit/")
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        input_form.send_keys("updated_tag2_name")
        button = self.browser.find_element_by_id("Update")
        button.click()

        content = self.browser.find_element_by_tag_name("ul")
        # Check if names were updated
        self.assertIn('updated_tag1_name', content.text)
        self.assertIn('updated_tag2_name', content.text)

    def test_user_creates_empty_name_tag_and_wants_to_save_it(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        # Leave field empty and try to save it
        button = self.browser.find_element_by_id("Update")
        button.click()

        # User is still on the same page, can't upload empty name tag.
        url = self.browser.current_url
        self.assertEqual(url, self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")

    def test_user_updates_to_long_tag_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        # Update more than 20 characters name
        input_form.send_keys("more_than_20_characters_string")
        button = self.browser.find_element_by_id("Update")
        button.click()

        content = self.browser.find_element_by_tag_name("ul")
        self.assertNotEqual('more_than_20_characters_string', content.text)

    def test_user_updates_20_characters_tag_name(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        # User goes to tag create page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/{tag1.id}/edit/")
        input_form = self.browser.find_element_by_css_selector('#id_name')
        # clear input_form field befoore updating
        input_form.clear()
        # Update exactly than 20 characters name
        input_form.send_keys("12345678901234567890")
        # save new tag to project.
        button = self.browser.find_element_by_id("Update")
        button.click()

        content = self.browser.find_element_by_tag_name("ul")
        self.assertEqual('12345678901234567890', content.text)
