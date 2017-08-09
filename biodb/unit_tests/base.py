from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project
from robjects.models import Robject


class FunctionalTest(TestCase):
    def login_default_user(self):
        user = User.objects.create_user(
            username="USERNAME", password="PASSWORD")
        self.client.login(username="USERNAME", password="PASSWORD")
        return user

    def default_set_up_for_robjects_page(self):
        user = self.login_default_user()
        proj = Project.objects.create(name="project_1")

        return user, proj
