from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project
from robjects.models import Robject
from django.core.urlresolvers import reverse, resolve
from guardian.shortcuts import assign_perm


class FunctionalTest(TestCase):
    # PERMISSIONS ERRORS
    VISIT_PERMISSION_ERROR = "User doesn't have permission: can visit project"

    # DEFAULT SHORTCUT URLS
    LOGIN_URL = reverse("login")
    PROJECT_LIST_URL = reverse("projects:projects_list")
    ROBJECT_LIST_URL = reverse("projects:robjects:robjects_list", kwargs={
                               "project_name": "project_1"})
    ROBJECT_DELETE_URL = reverse("projects:robjects:robject_delete", kwargs={
                                 "project_name": "project_1"})
    ROBJECT_EXCEL_URL = reverse("projects:robjects:raport_excel", kwargs={
        "project_name": "project_1"})
    ROBJECT_SEARCH_URL = reverse("projects:robjects:search_robjects",
                                 kwargs={"project_name": "project_1"})
    ROBJECT_HISTORY_URL = reverse(
        "projects:robjects:robject_history",
        kwargs={"project_name": "project_1", "robject_id": 1})
    ROBJECT_EDIT_URL = reverse("projects:robjects:robject_edit", kwargs={
        "project_name": "project_1",
        "robject_id": 1
    })
    ROBJECT_CREATE_URL = reverse("projects:robjects:robject_create",
                                 kwargs={"project_name": "project_1"})
    ROBJECT_PDF_URL = reverse("projects:robjects:pdf_raport",
                              kwargs={"project_name": "project_1"})
    TAG_CREATE_URL = reverse("projects:tag_create", kwargs={
                             "project_name": "project_1"})
    TAG_EDIT_URL = reverse("projects:tag_update",
                           kwargs={"project_name": "project_1", "tag_id": 1})
    TAG_DELETE_URL = reverse("projects:tag_delete",
                             kwargs={"project_name": "project_1", "tag_id": 1})
    TAG_LIST_URL = reverse("projects:tag_list",
                           kwargs={"project_name": "project_1"})
    SAMPLE_LIST_URL = reverse("projects:samples:sample_list",
                              kwargs={"project_name": "project_1"})
    SAMPLE_DETAILS_URL = reverse("projects:samples:sample_details",
                                 kwargs={"project_name": "project_1", "sample_id": 1})
    SAMPLE_EDIT_URL = reverse("projects:samples:sample_edit",
                              kwargs={"project_name": "project_1", "sample_id": 1})

    def default_set_up_for_projects_pages(self):
        user = User.objects.create_user(
            username="USERNAME", password="PASSWORD")
        self.client.login(username="USERNAME", password="PASSWORD")
        return user

    def default_set_up_for_visit_robjects_pages(self):
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name="project_1")
        assign_perm("projects.can_visit_project", user, proj)

        return user, proj

    def annonymous_testing_helper(self, requested_url):
        """ Helper method to use in annonymous redirections tests.
        """
        proj = Project.objects.create(name="project_1")
        response = self.client.get(requested_url)

        self.assertRedirects(
            response,
            reverse("login") + f"?next={requested_url}")

    def permission_testing_helper(self, url, error_message, preassigned_perms=[]):
        """ Helper method to use in perrmissions tests.

            Args:
                url: address of requested view
                error_message: message you expect to see when permission
                    valuation fails
                preassigned_perms: list of permissions already attached to user
        """
        user = self.default_set_up_for_projects_pages()
        proj = Project.objects.create(name="project_1")
        robj = Robject.objects.create(name="robject_1", project=proj)
        for perm in preassigned_perms:
            assign_perm(perm, user, proj)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(f"<h1>{error_message}</h1>", response.content.decode("utf-8"))

    def not_matching_url_kwarg_helper(self, requested_url):
        """ Function tests all variations of valid urls with not matching slugs

            Function tests all variations of urls. Single variation has all
            slugs matching except one.

            Example:
            Following urls will be tested (robject edit urls):
            1) /projects/<not_matching_project_name>/robjects/1/edit/
            2) /projects/project_1/robjects/<not_matching_robject_id>/edit/
        """
        # get ResolverMatch object
        match = resolve(requested_url)
        # get slug labels (project_name, robject_id etc.)
        kwargs = match.kwargs
        self.default_set_up_for_projects_pages()

        for name in kwargs:
            # create copy of kwargs dict
            amend_kwargs = dict(kwargs)
            if name == "project_name":
                amend_kwargs[name] = "random_project"
            else:
                amend_kwargs[name] = 123456789
            # create url with one slug not match
            new_path = reverse(match.app_name + ":" +
                               match.url_name, kwargs=amend_kwargs)
            response = self.client.get(new_path)
            self.assertIn("<h1>Not Found</h1>", str(response.content))
            self.assertIn(
                f"<p>The requested URL {new_path} was not found on this server.</p>",
                str(response.content))
