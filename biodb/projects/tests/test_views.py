from django.http import Http404
from projects.models import Project
from robjects.models import Robject
from projects.models import Tag
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


class TagsListViewTestCase(FunctionalTest):
    def test_renders_given_template(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        response = self.client.get("/projects/project_1/tags/")
        self.assertTemplateUsed(response, "tags/tag_list.html")

    def test_tags_in_correct_project(self):
        proj1 = Project.objects.create(name="project_1")
        proj2 = Project.objects.create(name="project_2")
        self.login_default_user()
        tag1 = Tag.objects.get_or_create(name='Tag1', project=proj1)
        tag2 = Tag.objects.get_or_create(name='Tag2', project=proj2)
        response = self.client.get("/projects/project_1/tags/")
        self.assertIn(tag1[0], response.context['tag_list'])
        self.assertNotIn(tag2[0], response.context['tag_list'])

    def test_allow_empty_tag_list(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        response = self.client.get("/projects/project_1/tags/")
        self.assertEqual(0, len(response.context['tag_list']))

    def test_login_requirement(self):
        proj1 = Project.objects.create(name="project_1")
        response = self.client.get("/projects/project_1/tags/")
        self.assertEqual(response.status_code, 403)

    def test_get_status_404_for_not_existed_project_name(self):
        self.login_default_user()
        response = self.client.get("/projects/random_project/tags/")
        self.assertEqual(response.status_code, 404)

    def test_get_status_404_for_no_project_name(self):
        self.login_default_user()
        response = self.client.get("/projects//tags/")


        self.assertEqual(response.status_code, 404)
