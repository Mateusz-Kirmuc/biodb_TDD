from django.contrib.auth.models import User
from django.test import Client
from io import BytesIO
from openpyxl import load_workbook
from projects.models import Project
from robjects.models import Robject
from samples.models import Sample
from unit_tests.base import FunctionalTest
from samples.views import SampleListView
from guardian.shortcuts import assign_perm
from django.core.urlresolvers import resolve, reverse
from samples.views import sample_create_view
from django.test import tag


class SampleListViewTest(FunctionalTest):
    def test_visit_permission(self):
        self.permission_testing_helper(
            self.SAMPLE_LIST_URL, self.VISIT_PERMISSION_ERROR)

    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_kwarg_helper(self.SAMPLE_LIST_URL)

    def test_anonymous_user_gets_samples_page(self):
        Project.objects.create(name="PROJECT_1")
        response = self.client.get("/projects/PROJECT_1/samples/")
        # redirections to biodb main page
        # it is redirected when using login_required decorator
        # when using LoginRequiredMixin there will be 403
        self.assertEqual(response.status_code, 302)
        # assert that client is still in login page
        self.assertIn('/accounts/login/?next=', response.url)

    def test_render_template_on_get(self):
        user, proj = self.default_set_up_for_visit_robjects_pages()
        assign_perm("projects.can_visit_project", user, proj)
        samp = Sample(code='1a2b3c')
        response = self.client.get(f"/projects/{proj.name}/samples/")
        self.assertTemplateUsed(response, "samples/samples_list.html")

    def test_view_get_list_of_samples_and_pass_it_to_context(self):
        user, proj = self.default_set_up_for_visit_robjects_pages()
        assign_perm("projects.can_visit_project", user, proj)

        robj = Robject.objects.create(name='robject', project=proj)

        samp1 = Sample.objects.create(code='1a1a', robject=robj)
        samp2 = Sample.objects.create(code='2a2a', robject=robj)
        samp3 = Sample.objects.create(code='3a3a', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/")

        self.assertIn(samp1, response.context["sample_list"])
        self.assertIn(samp2, response.context["sample_list"])
        self.assertIn(samp3, response.context["sample_list"])

    def test_function_used(self):
        user, proj = self.default_set_up_for_visit_robjects_pages()
        assign_perm("projects.can_visit_project", user, proj)

        robj = Robject.objects.create(name='robject', project=proj)

        samp1 = Sample.objects.create(code='1a1a', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/")

        self.assertEqual(response.resolver_match.func.__name__,
                         SampleListView.as_view().__name__)

    def test_context_data(self):
        user, proj = self.default_set_up_for_visit_robjects_pages()
        assign_perm("projects.can_visit_project", user, proj)

        robj = Robject.objects.create(name='robject', project=proj)

        samp1 = Sample.objects.create(code='1a1a', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/")
        self.assertEqual(proj, response.context['project'])


class SampleDetailViewTest(FunctionalTest):
    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_kwarg_helper(self.SAMPLE_DETAILS_URL)

    def create_sample_data(self):
        user, proj = self.default_set_up_for_visit_robjects_pages()
        robj = Robject.objects.create(name='Robject', project=proj)
        samp = Sample.objects.create(code='code', robject=robj)
        return(user, proj, robj, samp)

    def test_anonymous_user_is_redirected_to_login_page(self):
        proj = Project.objects.create(name='Project_1')
        robj = Robject.objects.create(name='Robject', project=proj)
        samp = Sample.objects.create(code='code', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/projects/{proj.name}/samples/{samp.id}/')

    def test_user_without_permision_seas_permission_denied(self):
        self.permission_testing_helper(
            self.SAMPLE_DETAILS_URL, self.VISIT_PERMISSION_ERROR)

    def test_render_template_on_get(self):
        user, proj, robj, samp = self.create_sample_data()
        assign_perm("projects.can_visit_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertTemplateUsed(response, "samples/sample_details.html")

    def test_view_pass_sample_to_context(self):
        user, proj, robj, samp = self.create_sample_data()
        assign_perm("projects.can_visit_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertEqual(samp, response.context["object"])

    def test_view_filter_sample_get_in_context(self):
        user = self.default_set_up_for_projects_pages()
        proj1 = Project.objects.create(name='Project_1')
        proj2 = Project.objects.create(name='Project_2')
        assign_perm("projects.can_visit_project", user, proj1)

        robj1 = Robject.objects.create(name='Robject1', project=proj1)
        robj2 = Robject.objects.create(name='Robject2', project=proj2)

        samp1 = Sample.objects.create(code="samp1", robject=robj1)
        samp2 = Sample.objects.create(code="samp_2", robject=robj2)

        response = self.client.get(f"/projects/{proj1.name}/samples/{samp1.id}/")
        responsed_sample = response.context['object']
        self.assertEqual(responsed_sample.code, "samp1")

        response = self.client.get(f"/projects/{proj1.name}/samples/{samp2.id}/")
        responsed_sample = response.context['object']
        self.assertEqual(responsed_sample.code, "samp_2")


@tag("ut_sample_create")
class SampleCreateViewTestCase(FunctionalTest):
    SAMPLE_CREATE_URL = reverse("projects:robjects:sample_create", kwargs={
                                "project_name": "project_1", "robject_id": "1"})

    def help_make_post_request_to_sample_create_view(self, data):
        Robject.objects.create()
        response = self.client.post(self.SAMPLE_CREATE_URL, data, follow=True)
        return response

    @tag("ut_sample_create_1")
    def test_sample_create_url_resolve_to_sample_create_view(self):
        found = resolve(self.SAMPLE_CREATE_URL)
        self.assertEqual(found.func, sample_create_view)

    def test_view_renders_sample_create_template(self):
        response = self.client.get(self.SAMPLE_CREATE_URL)
        self.assertTemplateUsed(response, "samples/sample_create.html")

    def test_view_creates_new_sample_on_post(self):
        self.assertEqual(Sample.objects.count(), 0)
        self.help_create_user_and_make_post(
            "USERNAME", post_data={"owner": "USERNAME"})
        self.assertEqual(Sample.objects.count(), 1)

    def test_view_redirects_on_post(self):
        response = self.help_create_user_and_make_post(
            username="USERNAME",
            password="PASSWORD",
            post_data={"owner": "USERNAME", "code": "12334"},
            log_user_in=True,
            assign_visit_permission=True
        )
        last_sample_id = Sample.objects.last().id
        expected_redirect_url = reverse(
            "projects:samples:sample_details",
            kwargs={"project_name": "project_1", "sample_id": last_sample_id})
        self.assertRedirects(response, expected_redirect_url)
        response = self.client.get(self.SAMPLE_DETAILS_URL)

    def test_sample_create_resolver_match_contains_url_name(self):
        found = resolve(self.SAMPLE_CREATE_URL)
        self.assertEqual(found.url_name, "sample_create")

    def test_view_save_sample_code_in_db(self):
        self.default_set_up_for_projects_pages()
        self.help_make_post_request_to_sample_create_view(
            {"code": "ABCD", "owner": "USERNAME"})
        sample = Sample.objects.last()
        self.assertEqual(sample.code, "ABCD")

    def test_view_attach_robject_to_new_sample(self):
        self.default_set_up_for_projects_pages()
        robj = Robject.objects.create()
        response = self.help_make_post_request_to_sample_create_view(
            {"code": "ABCD", "owner": "USERNAME"})
        sample = Sample.objects.last()
        self.assertIsNotNone(sample.robject)
        self.assertEqual(sample.robject, robj)

    def test_view_attach_owner_to_new_sample(self):
        self.default_set_up_for_projects_pages()
        self.help_make_post_request_to_sample_create_view(
            {"owner": "USERNAME"})
        sample = Sample.objects.last()
        self.assertEqual(sample.owner.username, "USERNAME")

    def test_view_assign_user_object_to_modify_by_field_in_sample(self):
        self.default_set_up_for_projects_pages()
        self.help_make_post_request_to_sample_create_view(
            {"code": "ABCD", "owner": "USERNAME"})
        sample = Sample.objects.last()
        self.assertEqual(sample.modify_by.username, "USERNAME")

    def test_view_pass_to_template_all_created_users(self):
        u_first = self.help_create_user(username="first_created_user")
        u_second = self.help_create_user(username="second_created_user")
        response = self.client.get(self.SAMPLE_CREATE_URL)
        self.assertEqual(len(response.context["owners"]), 2)
        self.assertIn(u_first, response.context["owners"])
        self.assertIn(u_second, response.context["owners"])

    def test_view_attach_authenticated_user_to_modify_by_sample_field(self):
        response, u = self.help_create_user_and_make_post(
            username="user", password="user_passwd",
            post_data={"owner": "user"}, return_user=True)
        self.assertEqual(Sample.objects.last().modify_by, None)
        self.client.login(username="user", password="user_passwd")
        response = self.help_make_post_request_to_sample_create_view(
            {"owner": "user"})
        self.assertEqual(Sample.objects.last().modify_by, u)

    def test_when_view_gets_empty_sample_code_it_renders_the_same_page(self):
        response = self.help_create_user_and_make_post(
            username="user_1", post_data={"code": "", "owner": "user_1"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "samples/sample_create.html")

    def help_create_user(self, username, password=None):
        return User.objects.create_user(username=username, password=password)

    def help_create_user_and_make_post(self, username, password=None,
                                       post_data={},
                                       log_user_in=False,
                                       return_user=False,
                                       assign_visit_permission=False):
        proj = Project.objects.create(name="project_1")
        user = self.help_create_user(username=username, password=password)
        if log_user_in:
            self.client.login(username=username, password=password)
        if assign_visit_permission:
            assign_perm("can_visit_project", user, proj)
        response = self.help_make_post_request_to_sample_create_view(post_data)
        if return_user:
            return response, user
        return response

    def test_view_passes_error_false_boolean_to_template_on_get(self):
        response = self.client.get(self.SAMPLE_CREATE_URL)
        self.assertEqual(response.context["error"], False)
