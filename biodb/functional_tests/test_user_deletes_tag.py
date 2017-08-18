import time
from datetime import datetime
from django.contrib.auth.models import User
from django.test import tag
from functional_tests.base import FunctionalTest
from projects.models import Project
from projects.models import Tag
from robjects.models import Robject
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


@tag('slow')
class UserVisitsDeleteTagPage(FunctionalTest):
    def test_user_checks_delete_tag_page(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag object
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # User goes directly to Tag delete page for sample tag
        self.browser.get(self.live_server_url +
                         f"/projects/PROJECT_1/tags/{tag1.id}/delete/")

        self.assertTemplateUsed('tags/tag_delete.html')

    def test_annonymous_user_visits_delete_tag_page(self):
        # To visit any tag page, project object needed.
        proj1 = Project.objects.create(name="PROJECT_1")
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # Anonymous user goes to tags/create page. He sees permission denied
        # message
        self.browser.get(self.live_server_url +
                         f"/projects/PROJECT_1/tags/{tag1.id}/delete/")
        # New in Django 1.11, decorator method instead of LoginRequiredMixin
        # Returns permited page for annonymous user not '403 Forbiden'
        head = self.browser.find_element_by_tag_name("h1")
        # Useer is redirected to home biodb page
        self.assertEqual(head.text, "Welcome to BioDB")

    def test_user_is_redirected_to_delete_tag_page(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag object
        tag1, created = Tag.objects.get_or_create(name='Tag', project=proj1)
        # User goes to list tag
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")
        # User clicks on delete button for specific tag
        button = self.browser.find_element_by_css_selector('.delete')
        button.click()

        self.assertTemplateUsed('tags/tag_delete.html')


@tag('slow')
class UserDeletesTag(FunctionalTest):

    def test_user_deletes_single_Tag_and_checks_tag_list(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag object
        tag1, created = Tag.objects.get_or_create(
            name='Tag_name', project=proj1)
        # User goes to list tag
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")
        # User clicks on delete button for specific tag
        button = self.browser.find_element_by_css_selector('.delete')
        button.click()
        # User is redirected to page in order to confirm tag deletion
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Are you sure you want to delete', body.text)
        # User is sure that it's a good idea
        button = self.browser.find_element_by_css_selector(
            'input[type="submit"]')
        button.click()
        self.assertTemplateUsed('tags/tag_list.html')
        # User checks if tag name is not on page
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Tag_name', body.text)

    @tag('now')
    def test_user_cretes_two_objetcs_and_deletes_one(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()
        # Create sample tag object
        tag1, created = Tag.objects.get_or_create(
            name='Tag_name', project=proj1)
        tag2, created = Tag.objects.get_or_create(
            name='Tag2_name', project=proj1)
        # User goes to list tag
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")
        # User clicks on first delete button for specific tag
        button = self.browser.find_element_by_css_selector('.delete')
        button.click()
        # User is redirected to page in order to confirm tag deletion
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Are you sure you want to delete', body.text)
        # User is sure that it's a good idea
        button = self.browser.find_element_by_css_selector(
            'input[type="submit"]')
        button.click()
        # self.assertTemplateUsed('tags/tag_list.html')
        # User checks if tag name is not on page
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Tag_name', body.text)
        # User checks if second tag is on page
        self.assertIn('Tag2_name', body.text)
