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
        user, proj = self.default_set_up_for_robjects_page()
        response = self.client.get(f"/projects/{proj.name}/robjects/")

        self.assertTemplateUsed(response, "projects/robjects_list.html")

    def test_view_create_list_of_robjects_and_pass_it_to_context(self):
        user, proj = self.default_set_up_for_robjects_page()

        robj1 = Robject.objects.create(author=user, project=proj)
        robj2 = Robject.objects.create(author=user, project=proj)
        robj3 = Robject.objects.create(author=user, project=proj)
        response = self.client.get(f"/projects/{proj.name}/robjects/")

        self.assertIn(robj1, response.context["robject_list"])
        self.assertIn(robj2, response.context["robject_list"])


class SearchRobjectsViewTests(FunctionalTest):
    def test_view_renders_robjects_page_template(self):
        user, proj = self.default_set_up_for_robjects_page()

        response = self.client.get(f"/projects/{proj.name}/robjects/search/",
                                   {"query": ""})
        self.assertTemplateUsed(response, "projects/robjects_list.html")

    def test_view_gets_valid_query_on_get__view_pass_qs_to_template(self):
        user, proj = self.default_set_up_for_robjects_page()

        robject_1 = Robject.objects.create(name="robject_1")
        robject_2 = Robject.objects.create(name="robject_2")

        response = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": "robject_1"})
        queryset = Robject.objects.filter(name="robject_1")
        # comparison of two querysets
        self.assertQuerysetEqual(
            response.context["robject_list"], map(repr, queryset))

    def test_annonymous_user_has_no_access_to_search_view(self):
        proj = Project.objects.create(name="project_1")

        resp = self.client.get(f"/projects/{proj.name}/robjects/search/")
        self.assertEqual(resp.status_code, 403)

    def test_view_can_perform_search_basing_on_part_of_robject_name(self):
        user, proj = self.default_set_up_for_robjects_page()

        robject_1 = Robject.objects.create(name="robject_1")
        robject_2 = Robject.objects.create(name="robject_2")

        response = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": "_1"})  # part!

        queryset = Robject.objects.filter(name="robject_1")

        # comparison of two querysets
        self.assertQuerysetEqual(
            response.context["robject_list"], map(repr, queryset))

    def test_search_is_case_insensitive(self):
        user, proj = self.default_set_up_for_robjects_page()

        robj = Robject.objects.create(name="RoBjEcT_1")

        # lower case query
        resp = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": "robject_1"})

        self.assertEqual(list(resp.context["robject_list"]),
                         [robj])

        # upper case query
        resp = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": "ROBJECT_1"})

        self.assertEqual(list(resp.context["robject_list"]),
                         [robj])

    def test_view_pass_project_name_to_context(self):
        user, proj = self.default_set_up_for_robjects_page()

        resp = self.client.get(f"/projects/{proj.name}/robjects/search/",
                               {"query": "robject_1"})

        self.assertEqual(proj.name, resp.context["project_name"])

    def test_search_include_full_author_name(self):
        user, proj = self.default_set_up_for_robjects_page()
        robj = Robject.objects.create(author=user)

        resp = self.client.get(f"/projects/{proj.name}/robjects/search/",
                               {"query": robj.author.username})

        self.assertIn(robj, resp.context["robject_list"])
