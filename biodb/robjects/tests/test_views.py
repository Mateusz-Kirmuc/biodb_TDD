from django.contrib.auth.models import User
from django.test import Client
from io import BytesIO
from openpyxl import load_workbook
from projects.models import Project
from robjects.models import Robject
from unit_tests.base import FunctionalTest


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


class Robjects_export_to_excel_view_test(FunctionalTest):
    def test_export_to_excel(self):
        # logged user goes to biodb to export a excel file
        user, proj = self.default_set_up_for_robjects_page()
        robj = Robject.objects.create(
            author=user, project=proj, name="robject_1")

        response = self.client.get(f"/projects/{proj.name}/robjects/{robj.id}/excel/")
        # assert attachment name as report.xlsx
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=report.xlsx")

        table_heder_list = ['id', 'project', 'author', 'name', 'create_by',
                            'create_date', 'modify_date', 'modify_by', 'notes',
                            'ligand', 'receptor', 'ref_seq', 'mod_seq',
                            'description', 'bibliography', 'ref_commercial',
                            'ref_clinical', 'files']
        #assert headers are the same as robject atrinutes names
        with BytesIO(response.content) as f:
            self.assertIsNotNone(f)
            wb = load_workbook(f)
            ws = wb.active
            first_row_cells = []
            for row in ws.rows:
                for cell in row:
                    first_row_cells.append(cell.value)
                break
        self.assertSequenceEqual(first_row_cells, table_heder_list)

        # if status code of requeszt is 200 -
        # The request was successfully received,
        # understood, and accepted
        self.assertEqual(response.status_code, 200)
    def test_export_to_excel(self):
        # logged user goes to biodb to export a excel file
        user, proj = self.default_set_up_for_robjects_page()
        robj = Robject.objects.create(
            author=user, project=proj, name="robject_1")

        response = self.client.get(f"/projects/{proj.name}/robjects/{robj.id}/excel/")
        # assert attachment name as report.xlsx
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=report.xlsx")

        table_heder_list = ['id', 'project', 'author', 'name', 'create_by',
                            'create_date', 'modify_date', 'modify_by', 'notes',
                            'ligand', 'receptor', 'ref_seq', 'mod_seq',
                            'description', 'bibliography', 'ref_commercial',
                            'ref_clinical', 'files']
        #assert headers are the same as robject atrinutes names
        with BytesIO(response.content) as f:
            self.assertIsNotNone(f)
            wb = load_workbook(f)
            ws = wb.active
            first_row_cells = []
            for row in ws.rows:
                for cell in row:
                    first_row_cells.append(cell.value)
                break
        self.assertSequenceEqual(first_row_cells, table_heder_list)

        # if status code of requeszt is 200 -
        # The request was successfully received,
        # understood, and accepted
        self.assertEqual(response.status_code, 200)
