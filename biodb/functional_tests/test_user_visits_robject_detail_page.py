from django.contrib.auth.models import User
from functional_tests.base import FunctionalTest
from projects.models import Project
from robjects.models import Robject
from robjects.models import Tag
from django.contrib.auth.models import User
from django.test import tag

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

@tag('slow')
class UserVisitRobjectDetailPage(FunctionalTest):
    def test_user_checks_robject_name(self):
        # Create sample project and robject
        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1")

        # User goes directly to robject detail page
        self.browser.get(
            self.live_server_url +
            f"/projects/{proj.name}/robjects/{robj1.id}/details")

        # User ckecks robject name
        names = self.browser.find_element_by_class_name('names')
        self.assertIn(str(robj1.name), names.text)

    def test_user_checks_robject_details(self):
        # Create sample project and robject
        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects and some additional detail informations
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1",
            notes='Notes, notes, notes',
            ligand='ligand_name',
            receptor='receptor_name',
            description='Rich Text Field description')

        # User goes directly to robject detail page
        self.browser.get(
            self.live_server_url +
            f"/projects/{proj.name}/robjects/{robj1.id}/details")

        # User checks details
        details = self.browser.find_element_by_class_name('details')
        detail_text = details.text
        self.assertIn('receptor_name', detail_text)
        self.assertIn('ligand_name', detail_text)

    def test_user_checks_tags(self):
        # Create sample project and robject
        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1")

        # Create sample Tag class object and conect it to sample proejct
        tag1 = Tag(name='tag1', project=proj)

        # User goes directly to robject detail page
        self.browser.get(
            self.live_server_url +
            f"/projects/{proj.name}/robjects/{robj1.id}/details")

        # User ckecks robject name
        tags = self.browser.find_element_by_class_name('tags')
        self.assertIn(str(tag1.name), 'tag1')
