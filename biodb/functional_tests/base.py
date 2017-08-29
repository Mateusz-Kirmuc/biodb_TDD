import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from projects.models import Project


class FunctionalTest(StaticLiveServerTestCase):
    MAX_WAIT = 10

    def setUp(self):
        self.browser = webdriver.Firefox()

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

    def login_user(self, username, password):
        """ Helper method for log user in.
        """
        try:
            u = User.objects.create_user(username=username, password=password)
        except IntegrityError:
            u = User.objects.get(username=username)
        self.browser.get(self.live_server_url)
        username_input = self.browser.find_element_by_css_selector(
            "#username_input")
        password_input = self.browser.find_element_by_css_selector(
            "#password_input")
        submit_button = self.browser.find_element_by_id("submit_button")

        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()
        expected_url = self.live_server_url + "/projects/"
        assert self.browser.current_url == expected_url, "User login failed!"

        return u

    def project_set_up_using_default_data(self):
        """ Helper method for all robject page related tests.

            Method include logged user with default creadentials and project
            with default name.
        """
        user = self.login_user("USERNAME", "PASSWORD")

        proj = Project.objects.create(name="project_1")

        self.browser.get(self.live_server_url + f"/projects/{proj}/robjects/")

        return user, proj

    def annonymous_user(self, page_url):
        '''Annonymous_user visites current page from page_url.

            Method tests if content of page is correct.
            when using decorators @login_required there will be no
            403 forbiden errorm

            Checks if the user is still on 'Welcome to BioDB' main page.
        '''
        self.browser.get(self.live_server_url + page_url)
        content = self.browser.find_element_by_tag_name("body")
        assertion = self.assertIn('Welcome to BioDB', content.text)
