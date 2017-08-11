from django.contrib.auth.models import User
from django.test import tag
from functional_tests.base import FunctionalTest
from selenium.common.exceptions import NoSuchElementException
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys


@tag('slow')
class UserLogoutTests(FunctionalTest):
    def test_logged_user_logs_out(self):
        # Create active user.

        usr = User.objects.create_user(username="UNAME", password="PASSWORD")

        # Login active user.

        self.login_user(username="UNAME", password="PASSWORD")

        # User gets to projects page. He wants to logout. He
        # clicks to logout button and is redirected to login page.

        self.browser.get(self.live_server_url + "/projects/")
        logout_button = self.browser.find_element_by_id("logout_button")
        logout_button.click()

        self.assertEqual(self.browser.current_url,
                         self.live_server_url + "/accounts/login/")

        # When he wants to get to projects page he sees permission denied
        # message.

        self.browser.get(self.live_server_url + "/projects/")
        body_element = self.browser.find_element_by_tag_name("body")
        self.assertEqual(body_element.text, "403 Forbidden")

    def test_annonymous_user_cant_find_logout_button(self):
        # Annonymous user goes to page he has access to. He looks for logout
        # button but he cant find it.
        self.browser.get(self.live_server_url + "/accounts/login/")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("logout_button")

        self.browser.get(self.live_server_url + "/accounts/sign-up/")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("logout_button")

    def test_annonymous_user_cant_get_to_logout_url(self):
        # Annonymous user wants to visit logout url. He is automatically
        # redirect to login page.
        self.browser.get(self.live_server_url + "/accounts/logout/")
        expected_current_url = self.live_server_url + "/accounts/login/"
        self.assertEqual(self.browser.current_url, expected_current_url)
