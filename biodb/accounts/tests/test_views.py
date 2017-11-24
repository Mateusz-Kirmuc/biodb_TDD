from unit_tests.base import FunctionalTest
from accounts.forms import SignUpForm
from django.core import mail
from biodb import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib import auth
from django.core.urlresolvers import reverse
from projects.models import Project
from guardian.shortcuts import assign_perm
# Create your tests here.


class LoginViewTests(FunctionalTest):
    def send_login_request(self, follow=False):
        response = self.client.post("/accounts/login/", {
            "username": "NapoleonBonaparte",
            "password": "liberte"
        }, follow=follow)
        return response

    def test_renders_welcome_template_on_get(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_redirect_after_valid_post(self):
        User.objects.create_user(
            username="NapoleonBonaparte",
            password="liberte"
        )
        response = self.send_login_request(follow=True)
        self.assertRedirects(response, "/projects/")

    def test_render_proper_template_if_validation_fails(self):
        response = self.send_login_request()
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_password_is_checked_during_credential_validation(self):
        User.objects.create_user(
            username="NapoleonBonaparte",
            password="liberte"
        )
        response = self.client.post("/accounts/login/", {
            "username": "NapoleonBonaparte",
            "password": "egalite"  # different password
        })
        self.assertEqual(response.status_code, 200)

    def test_form_exists_in_template_context_on_get(self):
        response = self.client.get("/accounts/login/")
        self.assertIn("form", response.context)

    def test_form_exists_in_template_context_on_invalid_post(self):
        response = self.client.post("/accounts/login/", {
            "username": "Elvis",
            "password": "rockandroll"
        })
        self.assertIn("form", response.context)

    def test_form_in_context_contain_error_message_after_credential_validation(self):
        response = self.client.post("/accounts/login/", {
            "username": "Elvis",
            "password": "rockandroll"
        })
        f = response.context["form"]
        self.assertEqual(f.errors["__all__"], [
                         "Invalid username or password."])

    def test_user_is_logged_after_view_call(self):
        user = User.objects.create_user(
            username="NapoleonBonaparte",
            password="liberte"
        )
        self.send_login_request()
        session_user = auth.get_user(self.client)
        self.assertEqual(user, session_user)

    def test_template_render_when_user_is_inactive(self):
        user = User.objects.create_user(
            username="NapoleonBonaparte",
            password="liberte",
        )
        user.is_active = False
        user.save()
        response = self.send_login_request()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_form_render_when_user_isnt_active(self):
        user = User.objects.create_user(
            username="NapoleonBonaparte",
            password="liberte",
        )
        user.is_active = False
        user.save()
        response = self.send_login_request()
        f = response.context["form"]
        self.assertEqual(f.errors["__all__"], [
                         "Invalid username or password."])

    def test_view_redirect_to_page_included_in_GET_data(self):
        project = Project.objects.create(name="project_1")
        url = f"{reverse('login')}?next={self.ROBJECT_LIST_URL}"
        user = User.objects.create_user(username="user_1", password="passwd_1")
        assign_perm("projects.can_visit_project", user, project)
        response = self.client.post(
            url, {"username": "user_1", "password": "passwd_1"})
        self.assertRedirects(response, self.ROBJECT_LIST_URL)


class SignUpViewTests(FunctionalTest):
    def test_render_valid_template_on_get(self):
        response = self.client.get("/accounts/sign-up/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/sign_up.html")

    def test_form_passed_to_template_context(self):
        response = self.client.get("/accounts/sign-up/")
        self.assertEqual(response.context["form"].__class__, SignUpForm)

    def test_display_errors_when_invalid_form_on_post(self):
        post_data = {
            "username": "",
            "email": "",
            "password": "",
            "confirm": ""
        }
        response = self.client.post("/accounts/sign-up/", post_data)
        self.assertTemplateUsed("accounts/sign-up.html")

        error_msg = "This field is required."
        for form_field in ["username", "email", "password", "confirm_password"]:
            self.assertFormError(response, "form", form_field, error_msg)

    def test_redirect_when_form_valid(self):
        credentials = {
            "username": "Pope Francis",
            "email": "holy@father.vt",
            "password": "habemus_papam",
            "confirm_password": "habemus_papam"
        }
        response = self.client.post("/accounts/sign-up/", credentials)
        self.assertRedirects(response, "/accounts/login/")

    def test_create_inactive_user_on_form_valid(self):
        credentials = {
            "username": "Pope Francis",
            "email": "holy@father.vt",
            "password": "habemus_papam",
            "confirm_password": "habemus_papam"
        }
        self.client.post("/accounts/sign-up/", credentials)
        user = User.objects.last()
        self.assertEqual(user.username, credentials["username"])
        self.assertEqual(user.email, credentials["email"])
        self.assertEqual(user.password, credentials["password"])
        self.assertFalse(user.is_active)

    def test_send_email_on_form_valid(self):
        credentials = {
            "username": "Pope Francis",
            "email": "holy@father.vt",
            "password": "habemus_papam",
            "confirm_password": "habemus_papam"
        }
        self.client.post("/accounts/sign-up/", credentials)
        user = User.objects.last()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "[BioDB] New user request for activation."
        )
        self.assertEqual(
            mail.outbox[0].body,
            "User with id={} request for activation.".format(user.id)
        )
        self.assertEqual(
            mail.outbox[0].to,
            [admin_data[1] for admin_data in settings.ADMINS]
        )


class LogoutViewTests(FunctionalTest):
    def test_view_logs_out_user(self):
        u = User.objects.create_user(username="USERNAME", password="PASSWORD")
        self.client.login(username="USERNAME", password="PASSWORD")
        response = self.client.get("/accounts/logout/")
        session_user = auth.get_user(self.client)
        self.assertNotEqual(session_user, u)
        self.assertIsInstance(session_user, AnonymousUser)

    def test_view_redirect_to_login_page(self):
        response = self.client.get("/accounts/logout/")
        self.assertRedirects(response, "/accounts/login/")
