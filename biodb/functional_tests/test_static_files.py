from django.contrib.auth.models import User
from django.test import tag

from functional_tests.base import FunctionalTest
from projects.models import Project
from robjects.models import Robject

@tag('slow')
class StaticFilesTests(FunctionalTest):
    def test_login_page(self):
        # User goes to login page.
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)
        # He noticed that login form is nicely centered.
        login_button = self.browser.find_element_by_id("submit_button")
        self.assertAlmostEqual(
            login_button.location["x"] + login_button.size["width"] / 2,
            512,
            delta=10
        )

    def test_robjects_list(self):
        # create user and log him in
        usr = User.objects.create_user(username="UNAME", password="PASSWORD")
        self.login_user(username="UNAME", password="PASSWORD")

        # create project
        proj = Project.objects.create(name="project_1")

        # create robject inside project
        Robject.objects.create(project=proj, author=usr)

        # User goes to robjects page.
        self.browser.get(self.live_server_url +
                         "/projects/project_1/robjects/")
        self.browser.set_window_size(1024, 768)

        # He noticed that robjects table is nicely centered.
        robjects_table = self.browser.find_element_by_css_selector(
            "#robjects_table")
        self.assertAlmostEqual(
            robjects_table.location["x"] + robjects_table.size["width"] / 2,
            512,
            delta=10)
