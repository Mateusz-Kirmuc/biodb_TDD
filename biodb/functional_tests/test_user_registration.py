from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import time
from functional_tests.base import FunctionalTest
from django.contrib.auth.models import User

class UserRegistrationTests(FunctionalTest):
    def test_registration_form(self):
        # User heard about biodb app and decide to visit this website. Received
        # adress leads him to welcome page. Welcome page contains welcome
        # message, login form with two fields and link to sign up form.
        self.browser.get(self.live_server_url)
        self.assertEqual(
            self.browser.current_url, self.live_server_url + "/accounts/login/"
        )
        header = self.browser.find_element_by_id("header")
        description = self.browser.find_element_by_id("description")
        self.assertEqual(
            header.text,
            "Welcome to BioDB"
        )
        self.assertEqual(
            description.text,
            "App that helps you manage your biological research"
        )
        login_form = self.browser.find_element_by_id("login_form")
        form_inputs = login_form.find_elements_by_tag_name("input")
        form_inputs_id = [input_.get_attribute("id") for input_ in form_inputs]
        for ID in ["login_input", "password_input"]:
            self.assertIn(ID, form_inputs_id)

        link = self.browser.find_element_by_id("sign_up_link")
        self.assertEqual(link.text, "Sign up")


        # Excited user clicks sign up link. Current relative url is:
        # '/accounts/sing-up/'.
        link.click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + "/accounts/sign-up/"
        )

        # User noticed new form with several fields: username, email adress,
        # password and repeat password and submit button. Each has its own
        # placeholder.

        sign_up_form = self.browser.find_element_by_id("sign_up_form")
        username_input = sign_up_form.find_element_by_id("username_input")
        email_input = sign_up_form.find_element_by_id("email_input")
        password_input = sign_up_form.find_element_by_id("password_input")
        confirm_input = sign_up_form.find_element_by_id("confirm_input")
        submit_button = sign_up_form.find_element_by_id("submit_button")

        self.assertEqual(
            username_input.get_attribute("placeholder"),
            "username"
        )
        self.assertEqual(
            email_input.get_attribute("placeholder"),
            "email"
        )
        self.assertEqual(
            password_input.get_attribute("placeholder"),
            "password"
        )
        self.assertEqual(
            confirm_input.get_attribute("placeholder"),
            "confirm password"
        )
        self.assertEqual(submit_button.text, "Submit")

        # Distracted user accidentaly clicks submit button before fill any
        # field. Instead of redirect he stays in the same page.
        current_url = self.browser.current_url
        submit_button.click()
        self.assertEqual(current_url, self.browser.current_url)

        # Now user sees error messages bound to every field.
        for el in ["username", "email", "password", "confirm_password"]:
            self.assertEqual(
                self.browser.find_element_by_id("{}_errorlist".format(el)).text,
                "This field is required."
            )

        # Immediately decides to repair his mistake and starts to fill the form
        # with data. But he dont know that user with such username already
        # exists in database. He quickly learns about it when he clicks submit
        # button. Above form appears following message:
        # 'User with such username or email already exists'.

        ## create user inside DB
        username = "Bilbo"
        email = "bilbo@baggins.shire.mde"
        password = "damn_dragon!"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        ## refresh page to delete previous form errors
        self.browser.get(self.live_server_url + "/accounts/sign-up/")


        sign_up_form = self.browser.find_element_by_id("sign_up_form")
        submit_button = sign_up_form.find_element_by_id("submit_button")
        input_ = sign_up_form.find_element_by_id("username_input")
        input_.send_keys('Bilbo')
        submit_button.click()

        error = self.browser.find_element_by_css_selector(
                                                      ".errorlist.nonfield").text

        self.assertEqual(
            error,
            "User with such username or email already exists".format(el)
        )

        # Curoius user decides to check if the same goes for email input. He
        # knows his fellow has account in BioDB and he knows his email. User
        # enter this email and looks for errors.

        ## refresh page to delete previous form errors
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        sign_up_form = self.browser.find_element_by_id("sign_up_form")
        submit_button = sign_up_form.find_element_by_id("submit_button")
        input_ = sign_up_form.find_element_by_id("email_input")
        input_.send_keys('bilbo@baggins.shire.mde')
        submit_button.click()

        error = self.browser.find_element_by_css_selector(
                                                      ".errorlist.nonfield").text

        self.assertEqual(
            error,
            "User with such username or email already exists".format(el)
        )

        # User fills form with new data and clicks submit button once again.
        # Success! He is redirected to a welcome page.
