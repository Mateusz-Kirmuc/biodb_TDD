import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from projects.models import Project
from django.core.urlresolvers import reverse, resolve
from guardian.shortcuts import assign_perm
from django.test import override_settings
from urllib.parse import urlparse
from robjects.models import Robject
from urllib.parse import urlparse


@override_settings(DEBUG=False)
class FunctionalTest(StaticLiveServerTestCase):
    """
        IMPORTANT!
        For the sake of simplicity please follow convention below:

        default project name: "project_1"
        default robject name: "robject_1"
        default sample name: "sample_1"
        default user username: "USERNAME"
        default user password: "PASSWORD"
    """
    MAX_WAIT = 10
    # DEFAULT SHORTCUT URLS

    @property
    def LOGIN_URL(self):
        return "/login/"

    @property
    def PROJECT_LIST_URL(self):
        return self.live_server_url + reverse("projects:projects_list")

    @property
    def ROBJECT_LIST_URL(self):
        return self.live_server_url + \
            reverse("projects:robjects:robjects_list",
                    kwargs={"project_name": "project_1"})

    @property
    def ROBJECT_DELETE_URL(self):
        return self.live_server_url + \
            reverse("projects:robjects:robject_delete",
                    kwargs={"project_name": "project_1"})

    @property
    def ROBJECT_EXCEL_URL(self):
        return self.live_server_url + reverse("projects:robjects:raport_excel",
                                              kwargs={"project_name": "project_1"})

    @property
    def ROBJECT_SEARCH_URL(self):
        return self.live_server_url + reverse("projects:robjects:search_robjects",
                                              kwargs={"project_name": "project_1"})

    @property
    def ROBJECT_HISTORY_URL(self):
        return self.live_server_url + reverse("projects:robjects:robject_history",
                                              kwargs={"project_name": "project_1", "robject_id": 1})

    @property
    def ROBJECT_EDIT_URL(self):
        return self.live_server_url + reverse("projects:robjects:robject_edit",
                                              kwargs={"project_name": "project_1", "robject_id": 1})

    @property
    def ROBJECT_CREATE_URL(self):
        return self.live_server_url + reverse("projects:robjects:robject_create",
                                              kwargs={"project_name": "project_1"})

    @property
    def ROBJECT_PDF_URL(self):
        return self.live_server_url + reverse("projects:robjects:pdf_raport",
                                              kwargs={"project_name": "project_1"})

    @property
    def TAG_CREATE_URL(self):
        return self.live_server_url + reverse("projects:tag_create", kwargs={
            "project_name": "project_1"})

    @property
    def TAG_EDIT_URL(self):
        return self.live_server_url + reverse("projects:tag_update",
                                              kwargs={"project_name": "project_1", "tag_id": 1})

    @property
    def TAG_DELETE_URL(self):
        return self.live_server_url + reverse("projects:tag_delete",
                                              kwargs={"project_name": "project_1", "tag_id": 1})

    @property
    def TAG_LIST_URL(self):
        return self.live_server_url + \
            reverse("projects:tag_list",
                    kwargs={"project_name": "project_1"})

    @property
    def SAMPLE_LIST_URL(self):
        return self.live_server_url + reverse("projects:samples:sample_list",
                                              kwargs={"project_name": "project_1"})

    @property
    def SAMPLE_DETAILS_URL(self):
        return self.live_server_url + reverse("projects:samples:sample_details",
                                              kwargs={"project_name": "project_1", "sample_id": 1})

    @property
    def SAMPLE_EDIT_URL(self):
        return self.live_server_url + reverse("projects:samples:sample_edit",
                                              kwargs={"project_name": "project_1", "sample_id": 1})

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.main_window = None
        while not self.main_window:
            self.main_window = self.browser.current_window_handle

    def tearDown(self):
        self.browser.quit()

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > self.MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def get_popup_window(self):
        popup_window = None
        while not popup_window:
            for handle in self.browser.window_handles:
                if handle != self.main_window:
                    popup_window = handle
                    break
        return popup_window

    def switch_to_popup(self):
        popup_window = self.get_popup_window()
        self.browser.switch_to.window(popup_window)

    def switch_to_main(self):
        self.browser.switch_to.window(self.main_window)

    def login_user(self, username, password):
        """ Helper method for log user in."""

        # It is better not to catch IntegrityError as it can happen
        # for other reasons.

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()

        self.browser.get(self.live_server_url + "/accounts/login/")
        username_input = self.browser.find_element_by_css_selector(
            "#username_input")
        password_input = self.browser.find_element_by_css_selector(
            "#password_input")
        submit_button = self.browser.find_element_by_id("submit_button")

        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()
        expected_url = self.live_server_url + "/projects/"
        assert self.browser.current_url == expected_url, f"User login failed!"

        return user

    # NOTE: THIS FUNCTION WILL BE REPLACED BY 'default_set_up_for_projects_pages'
    # IN FUTURE RELEASES!
    def project_set_up_and_get_robject_page(self, username="USERNAME",
                                            password="PASSWORD", project_name="project_1"):
        """ Helper method for all robject page related tests.
            Method include logged user with default creadentials and project
            with default name.
        """
        user = self.login_user(username, password)

        proj = Project.objects.create(name=project_name)

        self.browser.get(self.live_server_url + f"/projects/{proj}/robjects/")

        return user, proj

    def project_set_up_using_default_data(self, permission_visit=False,
                                          permission_modify=False):
        """ Helper method for all robject page related tests.
            Method include logged user with default creadentials and project
            with default name.
        """
        user = self.login_user("USERNAME", "PASSWORD")

        proj = Project.objects.create(name="project_1")

        if permission_visit:
            assign_perm("can_visit_project", user, proj)
        if permission_modify:
            assign_perm("can_modify_project", user, proj)

        self.browser.get(self.live_server_url + f"/projects/{proj}/robjects/")

        return user, proj

    # NOTE: THIS FUNCTION WILL BE REPLACED BY 'default_set_up_for_robjects_pages'
    # IN FUTURE RELEASES!
    def set_up_robject_list(self, project_name="project_1", username="username",
                            password="password", assign_visit_perm=True):
        proj = Project.objects.create(name=project_name)
        user = self.login_user(username, password)
        if assign_visit_perm:
            assign_perm("can_visit_project", user, proj)
        return proj, user

    def default_set_up_for_projects_pages(self):
        user = User.objects.create_user(
            username="USERNAME", password="PASSWORD")
        self.login_user("USERNAME", "PASSWORD")
        return user

    def default_set_up_for_robjects_pages(self):
        proj = Project.objects.create(name="project_1")
        user = self.default_set_up_for_projects_pages()
        assign_perm("can_visit_project", user, proj)
        return proj, user

    def default_url_robject_list(self):
        return self.live_server_url + reverse("projects:robjects:robjects_list", kwargs={"project_name": "project_1"})

    def annonymous_testing_helper(self, requested_url):
        # SET UP
        proj = Project.objects.create(name="project_1")

        # KEEP ONLY PATH FROM URL
        requested_path = urlparse(requested_url).path

        # Annonymous user goes to requested page
        self.browser.get(requested_url)

        # He is redirect to login page.
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url +
            reverse("login") + "?next=" + requested_path
        )

    def permission_view_testing_helper(self, requested_url):
        proj = Project.objects.create(name="project_1")
        user = User.objects.create_user(
            username="USERNAME", password="PASSWORD")
        robj = Robject.objects.create(name="robject_1", project=proj)
        self.login_user("USERNAME", "PASSWORD")

        self.browser.get(requested_url)
        h1 = self.browser.find_element_by_css_selector("h1")

        self.assertFalse(user.has_perm("projects.can_visit_project", proj))

        self.assertEqual(
            h1.text, "User doesn't have permission: can visit project")

    def not_matching_url_slug_helper(self, requested_url):
        """ Function tests all variations of valid urls with not matching slugs

            Function tests all variations of urls. Single variation has all
            slugs matching except one.

            Example:
            Following urls will be tested (robject edit urls):
            1) /projects/<not_matching_project_name>/robjects/1/edit/
            2) /projects/project_1/robjects/<not_matching_robject_id>/edit/
        """
        # get ResolverMatch object
        match = resolve(urlparse(requested_url).path)
        # get slug labels (project_name, robject_id etc.)
        kwargs = match.kwargs
        self.default_set_up_for_projects_pages()

        for name in kwargs:
            # create copy of kwargs dict
            amend_kwargs = dict(kwargs)
            if name == "project_name":
                amend_kwargs[name] = "random_project"
            else:
                amend_kwargs[name] = 123456789
            # create url with one slug not match
            new_path = reverse(match.app_name + ":" +
                               match.url_name, kwargs=amend_kwargs)

            self.browser.get(self.live_server_url + new_path)
            error_header = self.wait_for(
                lambda: self.browser.find_element_by_css_selector("h1"))
            error_text = self.wait_for(
                lambda: self.browser.find_element_by_css_selector("p"))
            self.assertEqual(error_header.text, "Not Found")
            self.assertEqual(
                error_text.text,
                f"The requested URL {new_path} was not found on this server.")
