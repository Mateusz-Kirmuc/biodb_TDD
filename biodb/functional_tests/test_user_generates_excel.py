from django.contrib.auth.models import User
from functional_tests.base import FunctionalTest
from projects.models import Project
from robjects.models import Robject
from robjects.models import Tag
from django.contrib.auth.models import User
from django.test import tag
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait as wait
import time
from selenium.webdriver.common.keys import Keys


@tag('slow')
class UserGeneratesExcel(FunctionalTest):
    def test_user_checks_output_file(self):
        # Create sample project and robject

        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects basic informations.
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1")
        # TODO: how to save this file, selenium is not
        # working with object other than htmls
        # get this url
        self.browser.get(
        self.live_server_url +
        f"/projects/{proj.name}/robjects/{robj1.id}/excel/")
