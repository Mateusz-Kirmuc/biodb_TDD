from django.contrib.auth.models import User
from django.test import tag
from functional_tests.base import FunctionalTest


@tag('slow')
class UserSignInTests(FunctionalTest):
    def __init__(self, *args, **kwargs):
        super(UserSignInTests, self).__init__(*args, **kwargs)
        self.username_input = lambda: self.browser.find_element_by_id(
            "username_input")
        self.password_input = lambda: self.browser.find_element_by_id(
            "password_input")
        self.submit_button = lambda: self.browser.find_element_by_id(
            "submit_button")

    def test_user_encounters_login_page(self):
        # User heard about biodb app and decide to visit this website. Received
        # adress leads him to welcome page. Welcome page contains welcome
        # message, login form with two fields and submit button and link
        # to sign up form.
        self.browser.get(self.live_server_url)
        self.assertEqual(
            self.browser.current_url, self.live_server_url + "/accounts/login/"
        )
        header = self.browser.find_element_by_id("header")
        description = self.browser.find_element_by_id("description")
        submit_button = self.browser.find_element_by_id("submit_button")
        self.assertEqual(
            header.text,
            "Welcome to BioDB"
        )
        self.assertEqual(
            description.text,
            "App that helps you manage your biological research"
        )
        self.assertEqual(
            self.username_input().get_attribute("id"), "username_input"
        )
        self.assertEqual(
            self.password_input().get_attribute("id"), "password_input"
        )

        self.assertEqual(submit_button.text, "Login")

        link = self.browser.find_element_by_id("sign_up_link")

        self.assertEqual(link.text, "Sign up")

    def test_user_logs_in_without_problems(self):
        # Create user inside Django DB
        user = User.objects.create_user(
            username="VitoCorleone", password="cosa_nostra")
        # User goes to BioDB adress. He is already signed-up so enters his
        # username and password and hit submit button. After succesful login
        # he get access to first BioDB page: "/projects/".
        self.browser.get(self.live_server_url)

        self.username_input().send_keys("VitoCorleone")
        self.password_input().send_keys("cosa_nostra")
        self.submit_button().click()
        self.assertEqual(
            self.browser.current_url, self.live_server_url + "/projects/")

    def test_user_encounters_invalid_credentials_validation(self):
        # User goes to BioDB application. He dont have account in BioDB but he
        # is curious what will happend when he enters fake user data. He sees
        # validation error above form.
        self.browser.get(self.live_server_url)

        self.username_input().send_keys("KingLion")
        self.password_input().send_keys("wrrrrau")
        self.submit_button().click()
        error_div = self.browser.find_element_by_css_selector(".nonfield li")
        self.assertEqual(
            "Invalid username or password.",
            error_div.text
        )

        # User decides to sign-up and take another test with login form. He
        # enters valid username and fake password and vice versa. He sees
        # excacly the same error in both cases.
        # create user in db
        user = User.objects.create_user(
            username="VitoCorleone", password="cosa_nostra")

        self.browser.get(self.live_server_url)

        self.username_input().send_keys("VitoCorleone")
        self.password_input().send_keys("vendetta")
        self.submit_button().click()

        error_div = self.browser.find_element_by_css_selector(".nonfield li")
        self.assertEqual(
            "Invalid username or password.",
            error_div.text
        )

    def test_user_encounters_required_field_validation(self):
        # User goes to Biodb application. He wants to find out what will
        # happend when he press submit button without fill any login field.
        # He gets validation error above any field in form.
        self.browser.get(self.live_server_url)
        self.submit_button().click()

        errors = self.browser.find_elements_by_class_name("errorlist")
        for error in list(errors):
            self.assertEqual(error.text, "This field is required.")

    def test_user_encounters_inactive_validation(self):
        # User goes to Biodb application. He is registered but admin didnt
        # activate his account. When user tries to log in,
        # he sees in-activation errors.
        user = User.objects.create_user(
            username="VitoCorleone", password="cosa_nostra")
        user.is_active = False
        user.save()
        self.browser.get(self.live_server_url)
        self.username_input().send_keys("VitoCorleone")
        self.password_input().send_keys("cosa_nostra")
        self.submit_button().click()

        error_div = self.browser.find_element_by_css_selector(".nonfield li")
        self.assertEqual(
            "Invalid username or password.",
            error_div.text
        )
