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
class UserVisitsDeleteTagPage(FunctionalTest):
    def test_checks_delete_tag_page(self):
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


@tag('slow')
class UserCreatesTag(FunctionalTest):
    pass
