from django.contrib.auth.models import User
from django.test import tag
from functional_tests.base import FunctionalTest
from selenium.common.exceptions import NoSuchElementException
# from selenium import webdriver
from selenium.webdriver.common.keys import Keys


@tag('slow')
class UserRegistrationTests(FunctionalTest):
    def setUp(self):
        super(UserRegistrationTests, self).setUp()

        def sign_up_form():
            return self.browser.find_element_by_id("sign_up_form")
        self.username_input = lambda: sign_up_form().find_element_by_id(
            "username_input")
        self.email_input = lambda: sign_up_form().find_element_by_id(
            "email_input")
        self.password_input = lambda: sign_up_form().find_element_by_id(
            "password_input")
        self.confirm_input = lambda: sign_up_form().find_element_by_id(
            "confirm_input")
        self.submit_button = lambda: sign_up_form().find_element_by_id(
            "submit_button")

    def test_user_use_sign_up_form_without_problems(self):
        # User heard about biodb app and decide to visit this website. Received
        # adress leads him to welcome page. Welcome page contains link to sign
        # up form.
        self.browser.get(self.live_server_url)

        link = self.browser.find_element_by_id("sign_up_link")

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

        self.assertEqual(
            self.username_input().get_attribute("placeholder"),
            "username"
        )
        self.assertEqual(
            self.email_input().get_attribute("placeholder"),
            "email"
        )
        self.assertEqual(
            self.password_input().get_attribute("placeholder"),
            "password"
        )
        self.assertEqual(
            self.confirm_input().get_attribute("placeholder"),
            "confirm password"
        )
        self.assertEqual(self.submit_button().text, "Submit")

        # Passwords fields are of type "password".
        self.assertEqual(
            self.password_input().get_attribute("type"), "password")
        self.assertEqual(
            self.confirm_input().get_attribute("type"), "password")

        # User is first user ever who sign-up to BioDB. He fills form with data
        # and click submit.
        credentials = {
            "username": "John Lenon",
            "email": "john.lennon@beatles.uk",
            "password": "i_m_the_best_beatle_paul",
        }
        self.username_input().send_keys(credentials["username"])
        self.email_input().send_keys(credentials["email"])
        self.password_input().send_keys(credentials["password"])
        self.confirm_input().send_keys(credentials["password"])
        self.submit_button().click()

        # Success! He is redirected to a login page.
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + "/accounts/login/"
        )

    def test_user_encounters_required_validation(self):
        # User goes stright to sign-up form page.
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        # Curoius user wants to know what will happend when he clicks submit
        # button before fill any field.Instead of redirect he stays in the same
        # page.
        current_url = self.browser.current_url
        self.submit_button().click()
        self.assertEqual(current_url, self.browser.current_url)

        # Now user sees error messages bound to every field.
        for el in ["username", "email", "password", "confirm_password"]:
            try:
                self.assertEqual(
                    self.browser.find_element_by_id(
                        "{}_errorlist".format(el)).text,
                    "This field is required."
                )
            except NoSuchElementException:
                if el == "confirm_password":
                    self.wait_for(
                        lambda: self.browser.find_element_by_css_selector(
                            "#confirm_input:invalid"
                        )
                    )
                else:
                    self.wait_for(
                        lambda: self.browser.find_element_by_css_selector(
                            "#" + el + "_input:invalid"
                        )
                    )

    def test_user_encounters_duplication_validation(self):
        # User goes to registration page of biodb.
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        # User suspect that form has data duplication validation. His close
        # fellow Bilbo Baggins has account in BioDB and user knows his
        # credentials. First he checks for username. Above form appears
        # following message: User with such username or email already exists'.

        # create Bilbo Baggins user

        username = "Bilbo"
        email = "bilbo@baggins.shire.mde"
        password = "damn_dragon!"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.username_input().send_keys('Bilbo')

        # rest of fields must be filled to prevent browser validation

        self.email_input().send_keys("test@test.com")
        self.password_input().send_keys("blabla")
        self.confirm_input().send_keys("blabla")
        self.submit_button().click()

        error = self.browser.find_element_by_css_selector(
            ".errorlist.nonfield").text

        self.assertEqual(
            error,
            "User with such username or email already exists"
        )

        # Curoius user decides to check if the same goes for email input. He
        #  User enters Bilbo's email and looks for errors.

        # refresh page to delete previous form errors
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        self.email_input().send_keys('bilbo@baggins.shire.mde')

        # rest of fields must be filled to prevent browser validation

        self.username_input().send_keys("cokolwiek")
        self.password_input().send_keys("blabla")
        self.confirm_input().send_keys("blabla")
        self.submit_button().click()

        error = self.browser.find_element_by_css_selector(
            ".errorlist.nonfield").text

        self.assertEqual(
            error,
            "User with such username or email already exists"
        )

    def test_user_encounters_password_validation(self):
        # User goes to sign-up page.
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        # User wants to check password validation. He enters different
        # passwords in both password fields and looks for error.

        # rest of fields must be filled to prevent browser validation

        self.username_input().send_keys("cokolwiek")
        self.email_input().send_keys("test@test.com")

        self.password_input().send_keys("top_secret")
        self.confirm_input().send_keys("less_secret")

        self.submit_button().send_keys(Keys.ENTER)
        error = self.wait_for(
            lambda: self.browser.find_element_by_css_selector(
                ".errorlist.nonfield").text
        )
        self.assertEqual(error, "Passwords doesn't match.")

    def test_user_encounters_duplication_and_password_validation(self):
        # User goes to sign-up page.
        self.browser.get(self.live_server_url + "/accounts/sign-up/")

        # User wonders what will happen if he commit two validation at once:
        # duplication and password. He fills appropriate fields with data
        # and looks for errors.

        # create Bilbo Baggins user
        username = "Bilbo"
        email = "bilbo@baggins.shire.mde"
        password = "damn_dragon!"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.username_input().send_keys('Bilbo')
        self.email_input().send_keys("test@test.com")  # any, test mail
        self.password_input().send_keys("top_secret")
        self.confirm_input().send_keys("less_secret")
        self.submit_button().click()

        errors = self.wait_for(
            lambda: self.browser.find_element_by_css_selector(
                ".errorlist.nonfield").text
        )
        self.assertIn("Passwords doesn't match.", errors)
        self.assertIn(
            "User with such username or email already exists", errors)

    def test_user_register_and_try_to_login(self):
        # User goes to register site. He enters all valid data and is redirect
        # to login page.
        self.browser.get(self.live_server_url + "/accounts/sign-up/")
        self.username_input().send_keys("JohnLenon")
        self.email_input().send_keys("john.lennon@beatles.uk")
        self.password_input().send_keys("i_m_the_best_beatle_paul")
        self.confirm_input().send_keys("i_m_the_best_beatle_paul")
        self.submit_button().click()

        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + "/accounts/login/"
        )

        # User tries to log in. Unfortunately he isnt allowed, becouse admin
        # needs to activate his account.
        login_username_input = self.browser.find_element_by_id(
            "username_input")
        login_password_input = self.browser.find_element_by_id(
            "password_input")
        submit_button = self.browser.find_element_by_id("submit_button")

        login_username_input.send_keys("JohnLenon")
        login_password_input.send_keys("i_m_the_best_beatle_paul")
        submit_button.click()

        error = self.browser.find_element_by_css_selector(".nonfield li")
        self.assertEqual(error.text, "Invalid username or password.")
