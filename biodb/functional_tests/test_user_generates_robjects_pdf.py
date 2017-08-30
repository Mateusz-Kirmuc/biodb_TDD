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
class UserVisitRobjecPDFGeneratePage(FunctionalTest):
    def test_logged_user_checks_robject_name(self):
        # Create sample project and robject
        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1")

        # User goes directly to robject raport_pdf page
        self.browser.get(
            self.live_server_url +
            f"/projects/{proj.name}/robjects/{robj1.id}/raport_pdf/")
        content = self.wait_for(
            lambda: self.browser.find_element_by_css_selector(".textLayer"))
        self.assertIn('robject_1', content.text)

    def test_annonymous_user_visits_pdf_page(self):
        # Create sample robjects basic informations.
        proj = Project.objects.create(name="project_1")
        robj1 = Robject.objects.create(project=proj, name="robject_1")
        robid = robj1.id
        # Annonymus user can not visit raport pdf page.
        self.annonymous_user("/projects/project_1/robjects/1/raport_pdf/")
