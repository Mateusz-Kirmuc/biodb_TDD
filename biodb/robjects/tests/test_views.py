from unit_tests.base import FunctionalTest
from robjects.models import Robject, Name, Tag
from projects.models import Project
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_addanother.widgets import AddAnotherWidgetWrapper
from django import forms
from django_addanother.views import CreatePopupMixin
from django.views import generic
from robjects.views import NameCreateView, TagCreateView
from biodb import settings
from guardian.shortcuts import assign_perm


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

        robject_1 = Robject.objects.create(name="robject_1", project=proj)
        robject_2 = Robject.objects.create(name="robject_2", project=proj)

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

        robject_1 = Robject.objects.create(name="robject_1", project=proj)
        robject_2 = Robject.objects.create(name="robject_2", project=proj)

        response = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": "object_1"})  # part!

        queryset = Robject.objects.filter(name="robject_1")

        # comparison of two querysets
        self.assertQuerysetEqual(
            response.context["robject_list"], map(repr, queryset))

    def test_search_is_case_insensitive(self):
        user, proj = self.default_set_up_for_robjects_page()

        robj = Robject.objects.create(name="RoBjEcT_1", project=proj)

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

    def create_sample_robject_and_send_query_to_search_view(self, project,
                                                            query,
                                                            **robject_kwargs):

        robj = Robject.objects.create(project=project, **robject_kwargs)
        resp = self.client.get(f"/projects/{project.name}/robjects/search/",
                               {"query": query})
        return robj, resp

    def create_sample_robject_search_for_it_and_confirm_results(
            self, query, robject_kwargs):
        user, proj = self.default_set_up_for_robjects_page()

        robj, resp = self.create_sample_robject_and_send_query_to_search_view(
            project=proj, query=query, **robject_kwargs)

        self.assertIn(robj, resp.context["robject_list"])

    def test_search_include_full_author_username(self):
        robject_kwargs = {
            "author": User.objects.create_user(username="AUTHOR")
        }
        self.create_sample_robject_search_for_it_and_confirm_results(
            query="AUTHOR",
            robject_kwargs=robject_kwargs
        )

    def test_search_include_fragment_author_username(self):
        robject_kwargs = {
            "author": User.objects.create_user(username="AUTHOR")
        }
        self.create_sample_robject_search_for_it_and_confirm_results(
            query="AUTH",
            robject_kwargs=robject_kwargs
        )

    def test_search_include_case_insensitive_full_author_username(self):
        robject_kwargs = {
            "author": User.objects.create_user(username="AUTHOR")
        }
        self.create_sample_robject_search_for_it_and_confirm_results(
            query="aUtHoR",
            robject_kwargs=robject_kwargs
        )

    def test_empty_query_will_display_all_robjects(self):
        user, proj = self.default_set_up_for_robjects_page()

        robj_1 = Robject.objects.create(project=proj)
        robj_2 = Robject.objects.create(project=proj)

        resp = self.client.get(
            f"/projects/{proj.name}/robjects/search/", {"query": ""})

        all_robjects = Robject.objects.filter(project=proj)

        self.assertEqual(
            list(resp.context["robject_list"]),
            list(all_robjects)
        )

    def test_search_include_robjects_from_given_project(self):
        user, proj = self.default_set_up_for_robjects_page()

        other_proj = Project.objects.create(name="other_proj")
        robj = Robject.objects.create(project=other_proj, name="robj")

        resp = self.client.get(
            f"/projects/{proj.name}/robjects/search/",
            {"query": f"{robj.name}"})

        self.assertNotIn(
            robj,
            list(resp.context["robject_list"])
        )


class RobjectCreateViewTestCase(FunctionalTest):
    def get_robject_create_url(self, proj):
        return reverse("robject_create", args=(proj.name,))

    def get_form_from_context(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.get(
            reverse("robject_create", args=(proj.name,)))
        form = response.context["form"]

        return form

    def test_renders_template(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.get(
            reverse("robject_create", args=(proj.name,)))
        self.assertTemplateUsed(
            response, template_name="robjects/robject_create.html")

    def test_renders_form_in_context(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.get(
            reverse("robject_create", args=(proj.name,)))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_model_class_is_Robject_in_form(self):
        form = self.get_form_from_context()
        self.assertEqual(form._meta.model, Robject)

    def test_widget_instance_of_names_field_in_form(self):
        form = self.get_form_from_context()
        self.assertIsInstance(
            form.base_fields["names"].widget, AddAnotherWidgetWrapper)

    def test_names_widget_arguments_in_form(self):
        form = self.get_form_from_context()
        widget = form.base_fields["names"].widget.widget
        add_related_url = form.base_fields["names"].widget.add_related_url
        self.assertIsInstance(widget, forms.SelectMultiple)
        self.assertEqual(add_related_url, reverse(
            "names_create", args=(Project.objects.last().name,)))

    def test_widget_instance_of_tags_field_in_form(self):
        form = self.get_form_from_context()
        self.assertIsInstance(
            form.base_fields["tags"].widget, AddAnotherWidgetWrapper)

    def test_tags_widget_arguments_in_form(self):
        form = self.get_form_from_context()
        widget = form.base_fields["tags"].widget.widget
        add_related_url = form.base_fields["tags"].widget.add_related_url
        self.assertIsInstance(widget, forms.SelectMultiple)
        self.assertEqual(add_related_url, reverse(
            "tags_create", args=(Project.objects.last().name,)))

    def test_view_redirects_to_robject_list_page_on_post(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.post(
            self.get_robject_create_url(proj),
            data={"name": "whatever"}
        )
        self.assertRedirects(response, reverse(
            "robjects_list", args=(proj.name,)))

    def test_name_field_is_required(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.post(
            self.get_robject_create_url(proj),
            data={"hello": "world"}  # request.POST pass, form.is_valid() fails
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            self.get_robject_create_url(proj),
            data={"name": "whatever"}
        )

        self.assertEqual(response.status_code, 302)

    def test_annonymous_user_is_redirect_to_login_page_on_get(self):
        proj = Project.objects.create(name="proj")
        response = self.client.get(self.get_robject_create_url(proj))

        self.assertRedirects(
            response,
            settings.LOGIN_URL + "?next=" + self.get_robject_create_url(proj)
        )

    def test_annonymous_user_is_redirect_to_login_page_on_post(self):
        proj = Project.objects.create(name="proj")
        response = self.client.post(self.get_robject_create_url(proj), data={})

        self.assertRedirects(
            response,
            settings.LOGIN_URL + "?next=" + self.get_robject_create_url(proj)
        )

    def test_user_without_project_mod_permission_gets_403_on_get(self):
        user, proj = self.default_set_up_for_robjects_page()
        response = self.client.get(self.get_robject_create_url(proj))

        self.assertEqual(response.status_code, 403)

    def test_view_removes_all_robject_less_names_on_get(self):
        Name.objects.create(name="name_1")
        Name.objects.create(name="name_2")
        self.assertEqual(Name.objects.filter(robjects=None).count(), 2)
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        self.client.get(self.get_robject_create_url(proj))
        self.assertEqual(Name.objects.filter(robjects=None).count(), 0)

    def test_rendered_form_has_no_create_by_field(self):
        form = self.get_form_from_context()
        self.assertNotIn("create_by", form.fields)

    def test_rendered_form_has_no_modify_by_field(self):
        form = self.get_form_from_context()
        self.assertNotIn("modify_by", form.fields)

    def test_rendered_form_has_no_create_date_field(self):
        form = self.get_form_from_context()
        self.assertNotIn("create_date", form.fields)

    def test_rendered_form_has_no_modify_date_field(self):
        form = self.get_form_from_context()
        self.assertNotIn("modify_date", form.fields)

    def test_view_assign_create_by_to_new_robject(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.post(
            self.get_robject_create_url(proj), {"name": "test"})
        r = Robject.objects.last()
        self.assertEqual(r.create_by, user)

    def test_view_assign_modify_by_to_new_robject(self):
        user, proj = self.default_set_up_for_robjects_page()
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.post(
            self.get_robject_create_url(proj), {"name": "test"})
        r = Robject.objects.last()
        self.assertEqual(r.modify_by, user)

    def test_project_field_from_context_form_is_hidden(self):
        form = self.get_form_from_context()
        self.assertTrue(form.fields["project"].widget.is_hidden)

    def test_project_field_from_context_form_initial(self):
        form = self.get_form_from_context()
        self.assertEqual(form.initial, {"project": Project.objects.first()})


class NameCreateViewTestCase(FunctionalTest):
    def get_names_create_url(self, proj):
        url = reverse("names_create", args=(proj.name,))
        return url

    def get_robject_create_url(self, proj):
        return reverse("robject_create", args=(proj.name,))

    def test_view_parents(self):
        self.assertEqual(NameCreateView.__bases__,
                         (CreatePopupMixin, generic.CreateView))

    def test_view_model_attr(self):
        self.assertEqual(NameCreateView.model, Name)

    def test_view_fields_attr(self):
        self.assertEqual(NameCreateView.fields, "__all__")

    def test_render_template(self):
        proj = Project.objects.create(name="proj_1")
        response = self.client.get(
            self.get_names_create_url(proj),
            HTTP_REFERER=self.get_robject_create_url(proj))
        self.assertTemplateUsed(response, "robjects/names_create.html")

    def test_view_return_400_when_requested_using_url(self):
        proj = Project.objects.create(name="proj_1")

        # Note: when form is open in popup window, request contains HTTP_REFERER
        # key in request.META dictionary. Otherwise, key doesn't exists.
        # HTTP_REFERER holds url to page from popup is open.

        # Test view gets request object without "HTTP_REFERER" key.
        response = self.client.get(self.get_names_create_url(proj))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "<h1>Error 400</h1><p>Form available from robject form only</p>",
            response.content.decode())

        # Test view gets request with META["HTTP_REFERER"].
        response = self.client.get(
            self.get_names_create_url(proj),
            HTTP_REFERER=self.get_robject_create_url(proj))
        self.assertEqual(response.status_code, 200)


class TagCreateViewTestCase(FunctionalTest):
    def get_tags_create_url(self, proj):
        url = reverse("tags_create", args=(proj.name,))
        return url

    def get_robject_create_url(self, proj):
        return reverse("robject_create", args=(proj.name,))

    def test_view_parents(self):
        self.assertEqual(TagCreateView.__bases__,
                         (CreatePopupMixin, generic.CreateView))

    def test_view_model_attr(self):
        self.assertEqual(TagCreateView.model, Tag)

    def test_render_template(self):
        proj = Project.objects.create(name="proj_1")
        response = self.client.get(reverse("tags_create", args=(
            proj.name,)), HTTP_REFERER=self.get_robject_create_url(proj))
        self.assertTemplateUsed(response, "robjects/tags_create.html")

    def test_view_renders_form_without_project_field(self):
        proj = Project.objects.create(name="proj_1")
        response = self.client.get(reverse("tags_create", args=(
            proj.name,)), HTTP_REFERER=self.get_robject_create_url(proj))
        self.assertNotIn("project", response.context["form"].fields)

    def test_project_is_assigned_automatically_in_view(self):
        proj = Project.objects.create(name="proj_1")
        self.client.post(
            reverse("tags_create", args=(proj.name,)), data={"name": "tag_name"},
            HTTP_REFERER=self.get_robject_create_url(proj))
        t = Tag.objects.last()
        self.assertEqual(t.name, "tag_name")
        self.assertEqual(t.project, proj)

    def test_view_return_400_when_requested_using_url(self):
        proj = Project.objects.create(name="proj_1")

        # Note: when form is open in popup window, request contains HTTP_REFERER
        # key in request.META dictionary. Otherwise, key doesn't exists.
        # HTTP_REFERER holds url to page from popup is open.

        # Test view gets request object without "HTTP_REFERER" key.
        response = self.client.get(self.get_tags_create_url(proj))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "<h1>Error 400</h1><p>Form available from robject form only</p>",
            response.content.decode())

        # Test view gets request with META["HTTP_REFERER"].
        response = self.client.get(
            self.get_tags_create_url(proj),
            HTTP_REFERER=self.get_robject_create_url(proj))
        self.assertEqual(response.status_code, 200)
