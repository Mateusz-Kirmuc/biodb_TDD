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
class UserGoesThrowAllTagPages(FunctionalTest):
    def test_user_creates_correct_tag_and_saves_it(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # User goes to tag page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")
        # User wants to create new tag.
        add_button = self.browser.find_element_by_id('add_button')
        add_button.click()
        # type correct tag name in name form.
        input_form = self.browser.find_element_by_css_selector('#id_name')
        input_form.send_keys("created_tag")
        # save new tag to project.
        button = self.browser.find_element_by_id("Save")
        button.click()

        # Check if tag is in tags list view.
        content = self.browser.find_element_by_tag_name("ul")
        self.assertIn('created_tag', content.text)

        # User wants to edit created tag.
        edit_button = self.browser.find_element_by_css_selector('a.edit')
        edit_button.click()
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

        # User wants to delate created and updated tag
        delete_button = self.browser.find_element_by_css_selector('a.delete')
        delete_button.click()
        # User is redirected to page in order to confirm tag deletion
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Are you sure you want to delete', body.text)
        # User is sure that it's a good idea
        button = self.browser.find_element_by_css_selector(
            'input[type="submit"]')
        button.click()
        self.browser.assertTemplateUsed('tags/tag_list.html')
        # User checks if tag name is not on page
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('updated_tag_name', body.text)
        self.assertTemplateUsed("projects/tag_list.html")
