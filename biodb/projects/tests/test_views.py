from projects.models import Project
from robjects.models import Tag
from unit_tests.base import FunctionalTest
from guardian.shortcuts import assign_perm


class ProjectListViewTestCase(FunctionalTest):

    def test_renders_given_template(self):
        self.default_set_up_for_projects_pages()
        response = self.client.get("/projects/")
        self.assertTemplateUsed(response, "projects/project_list.html")

    def test_pass_project_list_to_template_context(self):
        self.default_set_up_for_projects_pages()
        response = self.client.get("/projects/")
        self.assertIn("project_list", response.context)

    def test_get_project_list_from_db(self):
        proj1 = Project.objects.create(name="project_1")
        proj2 = Project.objects.create(name="project_2")
        self.default_set_up_for_projects_pages()
        response = self.client.get("/projects/")
        self.assertIn(proj1, response.context["project_list"])
        self.assertIn(proj2, response.context["project_list"])

    def test_login_requirement(self):
        self.annonymous_testing_helper(self.PROJECT_LIST_URL)


class TagListViewTestCase(FunctionalTest):
    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_slug_helper(self.TAG_LIST_URL)

    def test_anonymous_user_is_redirected_to_login_page(self):
        proj = Project.objects.create(name='Project_1')
        response = self.client.get(f"/projects/{proj.name}/tags/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/projects/{proj.name}/tags/')

    def test_template_used(self):
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        assign_perm("projects.can_visit_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/tags/")
        self.assertTemplateUsed(response, "projects/tags_list.html")

    def test_user_without_permision_seas_permission_denied(self):
        self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        response = self.client.get(f"/projects/{proj.name}/tags/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual("<h1>User doesn't have permission: can visit project</h1>",
                         response.content.decode("utf-8"))

    def test_view_pass_tag_list_to_context(self):
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        assign_perm("projects.can_visit_project", user, proj)
        tag1 = Tag.objects.create(name="t1", project=proj)
        tag2 = Tag.objects.create(name="t2", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/")
        self.assertIn("object_list", response.context)
        self.assertEqual(len(response.context["object_list"]), 2)
        self.assertIn(tag1, response.context["object_list"])
        self.assertIn(tag2, response.context["object_list"])

    def test_view_pass_project_name_to_context(self):
        user = self.default_set_up_for_projects_pages()
        proj1 = Project.objects.create(name='Project_1')
        proj2 = Project.objects.create(name='Project_2')
        assign_perm("projects.can_visit_project", user, proj1)
        assign_perm("projects.can_visit_project", user, proj2)
        tag1 = Tag.objects.create(name="t1", project=proj1)
        tag2 = Tag.objects.create(name="t2", project=proj2)
        response1 = self.client.get(f"/projects/{proj1.name}/tags/")
        self.assertIn("Project_1", response1.context["project_name"])
        response2 = self.client.get(f"/projects/{proj2.name}/tags/")
        self.assertIn("Project_2", response2.context["project_name"])

    def test_view_filter_tag_queryset_in_context(self):
        user = self.default_set_up_for_projects_pages()
        proj1 = Project.objects.create(name='Project_1')
        proj2 = Project.objects.create(name='Project_2')
        assign_perm("projects.can_visit_project", user, proj1)
        tag1 = Tag.objects.create(name="t1", project=proj1)
        tag2 = Tag.objects.create(name="t2", project=proj1)
        tag3 = Tag.objects.create(name="t_3", project=proj2)
        tag4 = Tag.objects.create(name="t_4", project=proj2)
        response = self.client.get(f"/projects/{proj1.name}/tags/")
        self.assertEqual(len(response.context["object_list"]), 2)
        self.assertIn(tag1, response.context["object_list"])
        self.assertIn(tag2, response.context["object_list"])


class TagCreateViewTest(FunctionalTest):
    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_slug_helper(self.TAG_CREATE_URL)

    def test_anonymous_user_is_redirected_to_login_page(self):
        proj = Project.objects.create(name='Project_1')
        response = self.client.get(f"/projects/{proj.name}/tags/create/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/projects/{proj.name}/tags/create/')

    def test_user_without_permision_seas_permission_denied(self):
        self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        response = self.client.get(f"/projects/{proj.name}/tags/create/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual("<h1>User doesn't have permission: can visit project</h1>",
                         response.content.decode("utf-8"))

    def test_view_pass_project_name_to_context(self):
        user = self.default_set_up_for_projects_pages()
        proj1 = Project.objects.create(name='Project_1')
        proj2 = Project.objects.create(name='Project_2')
        assign_perm("projects.can_visit_project", user, proj1)
        assign_perm("projects.can_modify_project", user, proj1)
        assign_perm("projects.can_visit_project", user, proj2)
        assign_perm("projects.can_modify_project", user, proj2)
        response1 = self.client.get(f"/projects/{proj1.name}/tags/create/")
        self.assertEqual(response1.status_code, 200)
        self.assertIn("Project_1", response1.context["project_name"])
        response2 = self.client.get(f"/projects/{proj2.name}/tags/create/")
        self.assertIn("Project_2", response2.context["project_name"])

    def test_form_valid_for_project(self):
        user = self.default_set_up_for_projects_pages()
        proj1 = Project.objects.create(name='Project_1')
        assign_perm("projects.can_visit_project", user, proj1)
        response = self.client.get(f"/projects/random_project/tags/create/")
        self.assertEqual(response.status_code, 404)
        self.assertInHTML("<h1>Not Found</h1>", str(response.content))


class TagUpdateViewTestCase(FunctionalTest):
    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_slug_helper(self.TAG_EDIT_URL)

    def test_anonymous_user_is_redirected_to_login_page(self):
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/edit/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/projects/{proj.name}/tags/{tag1.id}/edit/')

    def test_template_used(self):
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        assign_perm("projects.can_visit_project", user, proj)
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/edit/")
        self.assertTemplateUsed(response, "projects/tag_update.html")

    def test_user_without_permision_sees_permission_denied(self):
        self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/edit/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual("<h1>User doesn't have permission: can visit project</h1>",
                         response.content.decode("utf-8"))


class TagDeleteViewTestCase(FunctionalTest):
    def test_view_returns_404_when_slug_not_match(self):
        self.not_matching_url_slug_helper(self.TAG_DELETE_URL)

    def test_anonymous_user_is_redirected_to_login_page(self):
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/projects/{proj.name}/tags/{tag1.id}/delete/')

    def test_template_used(self):
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        assign_perm("projects.can_visit_project", user, proj)
        assign_perm("projects.can_modify_project", user, proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/delete/")
        self.assertTemplateUsed(response, "projects/tag_delete.html")

    def test_user_without_permision_seas_permission_denied(self):
        self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/delete/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual("<h1>403 Forbidden</h1>",
                         response.content.decode("utf-8"))

    def test_succes_url(self):
        self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name='Project_1')
        tag1 = Tag.objects.create(name="t1", project=proj)
        response = self.client.get(f"/projects/{proj.name}/tags/{tag1.id}/delete/")
