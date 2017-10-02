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


class SampleListViewTest(FunctionalTest):
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
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_visit_project", user, proj)
        samp = Sample(code='1a2b3c')
        response = self.client.get(f"/projects/{proj.name}/samples/")
        self.assertTemplateUsed(response, "samples/samples_list.html")

    def test_view_get_list_of_samples_and_pass_it_to_context(self):
        user, proj = self.default_set_up_for_robjects_page()
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
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_visit_project", user, proj)

        robj = Robject.objects.create(name='robject', project=proj)

        samp1 = Sample.objects.create(code='1a1a', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/")

        self.assertEqual(response.resolver_match.func.__name__,
                         SampleListView.as_view().__name__)

    def test_context_data(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_visit_project", user, proj)

        robj = Robject.objects.create(name='robject', project=proj)

        samp1 = Sample.objects.create(code='1a1a', robject=robj)
        response = self.client.get(f"/projects/{proj.name}/samples/")
        self.assertEqual(proj, response.context['project'])


class SampleDetailViewTest(FunctionalTest):
    def create_sample_data(self):
        user, proj = self.default_set_up_for_robjects_page()
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
        user, proj, robj, samp = self.create_sample_data()
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual("<h1>403 Forbidden</h1>",
                         response.content.decode("utf-8"))

    def test_render_template_on_get(self):
        user, proj, robj, samp = self.create_sample_data()
        assign_perm("projects.can_visit_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertTemplateUsed(response, "samples/sample_details.html")

    def test_view_pass_sample_to_context(self):
        user, proj, robj, samp = self.create_sample_data()
        assign_perm("projects.can_visit_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/samples/{samp.id}/")
        self.assertEqual(samp, response.context["sample"])

    def test_view_filter_sample_get_in_context(self):
        user = self.login_default_user()
        proj1 = Project.objects.create(name='Project_1')
        proj2 = Project.objects.create(name='Project_2')
        assign_perm("projects.can_visit_project", user, proj1)

        robj1 = Robject.objects.create(name='Robject1', project=proj1)
        robj2 = Robject.objects.create(name='Robject2', project=proj2)

        samp1 = Sample.objects.create(code="samp1", robject=robj1)
        samp2 = Sample.objects.create(code="samp_2", robject=robj2)

        response = self.client.get(f"/projects/{proj1.name}/samples/{samp1.id}/")
        responsed_sample = response.context['sample']
        self.assertEqual(responsed_sample.code, "samp1")

        response = self.client.get(f"/projects/{proj1.name}/samples/{samp2.id}/")
        responsed_sample = response.context['sample']
        self.assertEqual(responsed_sample.code, "samp_2")
