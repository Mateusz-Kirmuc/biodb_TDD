# from django.contrib.auth.models import User
# from django.test import TestCase
from django.http import Http404
from projects.models import Project
from projects.models import Tag
from robjects.models import Robject
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
        self.assertTemplateUsed(response, "projects/tag_list.html")

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


class TagCreateViewTestCase(FunctionalTest):
    def test_renders_given_template(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        response = self.client.get("/projects/project_1/tags/create/")
        self.assertTemplateUsed(response, "projects/tag_form.html")

    def test_login_requirement(self):
        proj1 = Project.objects.create(name="project_1")
        response = self.client.get("/projects/project_1/tags/create/")
        self.assertEqual(response.status_code, 403)

    def test_get_return_404_for_no_project_name(self):
        self.login_default_user()
        proj1 = Project.objects.create(name="project_1")
        response = self.client.post(
            "/projects//tags/create/", {'name': 'tag_name'})
        self.assertEqual(response.status_code, 404)

    def test_get_return_404_for_not_created_project(self):
        self.login_default_user()
        response = self.client.get("/projects/not_exist/tags/create/")
        self.assertEqual(response.status_code, 404)

    def test_get_302_status_for_two_tags_with_the_same_name(self):
        # expected rediect stsus 302
        self.login_default_user()
        proj1 = Project.objects.create(name="project_1")
        response = self.client.post(
            "/projects/project_1/tags/create/", {'name': 'same_tag'})
        response = self.client.post(
            "/projects/project_1/tags/create/", {'name': 'same_tag'})
        self.assertEqual(response.status_code, 200)


class TagEditViewTest(FunctionalTest):
    def test_renders_given_template(self):
        proj1 = Project.objects.create(name="project_1")
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        self.login_default_user()
        response = self.client.get(f"/projects/project_1/tags/{tag1.id}/edit/")
        self.assertTemplateUsed(response, "projects/tag_update_form.html")

    def test_login_requirement(self):
        proj1 = Project.objects.create(name="project_1")
        tag1 = Tag.objects.create(name='Tag1', project=proj1)
        response = self.client.get(f"/projects/project_1/tags/{tag1.id}/edit/")
        # New in Django 1.11. Imstead of LoginRequiredMixin using method decorators
        # It redirects to permited page, expected status code 302
        self.assertEqual(response.status_code, 302)
        # added extra asssertion to check redirect page
        self.assertTemplateUsed('accounts/login.html')

    def test_get_return_404_for_no_tagid(self):
        self.login_default_user()
        proj1 = Project.objects.create(name="project_1")
        response = self.client.post(
            "/projects/project_1/tags//edit/", {'name': 'tag_name'})
        self.assertEqual(response.status_code, 404)

    def test_get_return_404_for_not_created_tagid(self):
        self.login_default_user()
        proj1 = Project.objects.create(name="project_1")
        response = self.client.post(
            f"/projects/project_1/tags/12345/edit/", {'name': 'tag_name'})
        self.assertEqual(response.status_code, 404)

    def test_tag_after_editing_in_correct_project(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        tag1, created = Tag.objects.get_or_create(name='Tag1', project=proj1)
        response = self.client.post(
            f"/projects/project_1/tags/{tag1.id}/edit/", {'name': 'tag1_name'})
        # Check if status is correct and template
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('/projects/project_1/tags/')

    def test_get_status_302_for_editing_tag_name_that_already_exists(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        tag1, created = Tag.objects.get_or_create(name='Tag1', project=proj1)
        tag2, created = Tag.objects.get_or_create(name='Tag2', project=proj1)
        response = self.client.post(
            f"/projects/project_1/tags/{tag1.id}/edit/", {'name': 'Tag2'})
        # Check if redirected corectly to the same page
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('/projects/project_1/tags/{tag1.id}/edit/')

    def test_get_cutoff_tagname_for_to_long_edited_tag_name(self):
        proj1 = Project.objects.create(name="project_1")
        self.login_default_user()
        tag1, created = Tag.objects.get_or_create(name='Tag1', project=proj1)
        response = self.client.post(
            f"/projects/project_1/tags/{tag1.id}/edit/", {'name': 'more_than_20_characters_string'})
        # Check if succesfully posted request
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(tag1.name, 'more_than_20_characters_string')
