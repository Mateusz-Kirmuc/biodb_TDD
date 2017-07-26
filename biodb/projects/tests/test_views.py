# from django.contrib.auth.models import User
# from django.test import TestCase
from projects.models import Project
from projects.models import Robject
from unit_tests.base import FunctionalTest


class ProjectListViewTestCase(FunctionalTest):
    def test_renders_given_template(self):
        self.login_default_user()
        response = self.client.get("/projects/")
        self.assertTemplateUsed(response, "projects/project_list.html")

    def test_pass_project_list_to_template_context(self):
        self.login_default_user()
        response = self.client.get("/projects/")
        self.assertIn("project_list", response.context)

    def test_get_project_list_from_db(self):
        proj1 = Project.objects.create(name="project_1")
        proj2 = Project.objects.create(name="project_2")
        self.login_default_user()
        response = self.client.get("/projects/")
        self.assertIn(proj1, response.context["project_list"])
        self.assertIn(proj2, response.context["project_list"])

    def test_login_requirement(self):
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 403)


class RObjectsListViewTests(FunctionalTest):
    def test_anonymous_user_gets_robjects_page(self):
        Project.objects.create(name="PROJECT_1")
        response = self.client.get("/projects/PROJECT_1/robjects/")
        self.assertEqual(response.status_code, 403)

    def test_render_template_on_get(self):
        Project.objects.create(name="PROJECT_1")
        self.login_default_user()
        response = self.client.get("/projects/PROJECT_1/robjects/")

        self.assertTemplateUsed(response, "projects/robjects_list.html")

    def test_view_create_list_of_robjects_and_pass_it_to_context(self):
        usr = self.login_default_user()
        proj1 = Project.objects.create(name="project_1")
        proj2 = Project.objects.create(name="project_2")
        robj1 = Robject.objects.create(author=usr, project=proj1)
        robj2 = Robject.objects.create(author=usr, project=proj1)
        robj3 = Robject.objects.create(author=usr, project=proj2)
        response = self.client.get("/projects/project_1/robjects/")
        self.assertIn(robj1, response.context["robject_list"])
        self.assertIn(robj2, response.context["robject_list"])
        response = self.client.get("/projects/project_2/robjects/")
        self.assertIn(robj3, response.context["robject_list"])

    # def test_robject_list_is_in_template_context(self):
    #     pass
