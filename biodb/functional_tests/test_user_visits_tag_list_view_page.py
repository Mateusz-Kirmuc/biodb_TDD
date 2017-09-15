# import time
# from datetime import datetime
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
class UserVisitTagsPage(FunctionalTest):
    def test_annonymous_user_visit_tags_page(self):
        # To visit any robjects page, project object needed.
        Project.objects.create(name="PROJECT_1")
        # Anonymous user goes to tags page. He sees permission denied
        # message
        self.browser.get(self.live_server_url +
                         "/projects/PROJECT_1/tags/")
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(body.text, "403 Forbidden")

    def test_logged_user_checks_current_project_tags(self):
        # Create sample user, project
        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # Create sample Tag class objects and conect it to proejct
        tag1 = Tag.objects.get_or_create(name='Tag1', project=proj1)
        tag2 = Tag.objects.get_or_create(name='Tag2', project=proj1)

        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")

        # user checks header
        h1 = self.browser.find_element_by_tag_name("h1")
        self.assertIn("Tags:", h1.text)

        # user checks if all added tags to prject are visable
        tags_section = self.browser.find_element_by_class_name("tag_list")
        tag_list = tags_section.find_elements_by_tag_name("li")
        self.assertEqual(len(tag_list), 2)

    def test_logged_user_checks_only_current_project_tags(self):
        # Create sample user, project
        # Create sample project and robject

        usr1, proj1 = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr1, project=proj1, name="robject_1")

        # Create sample Tag class objects and conect it to proejct
        tag1 = Tag.objects.get_or_create(name='Tag1', project=proj1)
        tag2 = Tag.objects.get_or_create(name='Tag2', project=proj1)

        # Create other project and add tag to it
        other_project, created = Project.objects.get_or_create(name="test1")
        tag3 = Tag.objects.create(name='Tag3', project=other_project)

        self.browser.get(self.live_server_url +
                         f"/projects/{proj1.name}/tags/")

        # user checks header
        h1 = self.browser.find_element_by_tag_name("h1")
        self.assertIn("Tags:", h1.text)

        # user checks if tags are from current project
        tags_section = self.browser.find_element_by_class_name("tag_list")
        tag_list = tags_section.find_elements_by_tag_name("li")
        self.assertEqual(len(tag_list), 2)
