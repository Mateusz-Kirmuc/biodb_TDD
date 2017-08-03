# import time
# from datetime import datetime
from django.contrib.auth.models import User
from functional_tests.base import FunctionalTest
from projects.models import Project
from datetime import datetime
from django.contrib.auth.models import User
from robjects.models import Robject
import time


class UserVisitRobjectsPage(FunctionalTest):
    def test_annonymous_user_visit_robjects_page(self):
        # To visit any robjects page, project object needed.
        Project.objects.create(name="PROJECT_1")
        # Anonymous user goes to robjects page. He sees permission denied
        # message
        self.browser.get(self.live_server_url +
                         "/projects/PROJECT_1/robjects/")
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(body.text, "403 Forbidden")

    def test_logged_user_visit_robjects_page___no_robjects_exists(self):
        user, proj = self.project_set_up_using_default_data()

        # Logged user visit robjects page. He sees robjects table. Table has
        # several columns: robject id, robject name, robject create date,
        # robject author.
        self.browser.get(
            self.live_server_url + f"/projects/{proj.name}/robjects")
        header_row = self.browser.find_element_by_id("header_row")
        table_columns = header_row.find_elements_by_tag_name("th")
        table_columns_names = [column.text for column in table_columns]

        self.assertIn("id", table_columns_names)
        self.assertIn("name", table_columns_names)
        self.assertIn("author", table_columns_names)
        self.assertIn("create by", table_columns_names)
        self.assertIn("create date", table_columns_names)
        self.assertIn("modify by", table_columns_names)

        # Table hasnt any rows
        robject_rows = self.browser.find_elements_by_css_selector(
            ".row.robject")
        self.assertEqual(len(robject_rows), 0)

    def test_logged_user_visit_robjects_page___robjects_exists_in_project(self):
        usr, proj = self.project_set_up_using_default_data()

        # Create sample robjects.
        robj1 = Robject.objects.create(
            author=usr, project=proj, name="robject_1")
        robj2 = Robject.objects.create(
            author=usr, project=proj, name="robject_2")
        robj3 = Robject.objects.create(
            author=usr, project=proj, name="robject_3")

        # Logged user goes to project_1's robjects page. He knows that this
        # project contains several robjects. He sees table of rows. Each row
        # contains data of singe robject from this project.

        self.browser.get(self.live_server_url + "/projects/project_1/robjects")
        # rows has class names : "row robject_<robject pk>"
        # capture all rows
        robject_rows = self.browser.find_elements_by_css_selector(
            ".row")
        self.assertEqual(len(robject_rows), 3)

        for robject in [robj1, robj2, robj3]:
            # capture specific row
            row = self.browser.find_element_by_class_name(robject.name)
            self.assertIn(str(robject.id), row.text)
            self.assertIn(str(robject.author), row.text)


class SearchEngineTests(FunctionalTest):
    def __init__(self, *args, **kwargs):
        super(SearchEngineTests, self).__init__(*args, **kwargs)

        self.search_input = lambda: self.browser.find_element_by_id(
            "search_input")
        self.search_button = lambda: self.browser.find_element_by_id(
            "search_button")

    def send_query(self, query):
        self.search_input().send_keys(query)
        self.search_button().click()

    def look_for_robject_row(self, css):
        self.browser.find_element_by_css_selector(css)

    def create_sample_robject_and_go_to_robjects_page(self,
                                                      project,
                                                      **robject_kwargs):
        # Create sample robject.
        robj = Robject.objects.create(project=project, **robject_kwargs)

        # User goes to robjects page.
        self.browser.get(self.live_server_url +
                         f"/projects/{project.name}/robjects/")
        return robj

    def test_user_perform_search_based_on_whole_robj_name_and_find_robject(self):
        user, project = self.project_set_up_using_default_data()

        # Create sample robjects.
        Robject.objects.create(name="robject_1", project=project, id=1)
        Robject.objects.create(name="robject_2", project=project, id=2)

        # User goes to robjects page.
        self.browser.get(self.live_server_url +
                         "/projects/project_1/robjects/")

        # He sees two robjects in table.
        self.wait_for(
            lambda: self.browser.find_element_by_css_selector(".row.robject_1"))
        self.browser.find_element_by_css_selector(".row.robject_2")

        # User wants to test search tool. He looks for search form.
        search_form = self.browser.find_element_by_id("search_form")

        # User enter name of one robject and expect to see only this robject in
        # table.
        self.search_input().send_keys("robject_1")
        self.search_button().click()

        rows = self.browser.find_elements_by_css_selector(".row")
        self.assertEqual(len(rows), 1)

        self.browser.find_elements_by_css_selector(".robject_1")

    def test_user_search_for_one_robject_using_name_fragment(self):
        # Default setup for robjects page.
        user, proj = self.project_set_up_using_default_data()

        # Create sample robjects.
        Robject.objects.create(name="robject_1", project=proj)
        Robject.objects.create(name="robject_2", project=proj)

        # User would like to know if he can get search results using part of
        # robject name. To find out he goes to robjects page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj.name}/robjects/")

        # He sees two robjects in table.
        self.wait_for(
            lambda: self.browser.find_element_by_css_selector(".row.robject_1"))
        self.browser.find_element_by_css_selector(".row.robject_2")

        # He wants to search for robject with lower id. User enters part of its
        # name and looks for results.
        self.search_input().send_keys("_1")
        self.search_button().click()

        rows = self.browser.find_elements_by_css_selector(".row")
        self.assertEqual(len(rows), 1)

        self.browser.find_elements_by_css_selector(".robject_1")

    def test_user_search_for_multiple_robjects_using_name_fragment(self):
        # Make set up for robjects page.
        user, proj = self.project_set_up_using_default_data()

        # Create sample robjects.
        Robject.objects.create(name="robject_1", project=proj)
        Robject.objects.create(name="robject_2", project=proj)
        Robject.objects.create(name="foo", project=proj)

        # User want to find multiple robjects using common part of robject
        # names. He goes to robjects page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj.name}/robjects/")

        # User sees three robjects in table.
        table_rows = self.browser.find_elements_by_class_name("row")
        self.assertEqual(len(table_rows), 3)

        # Then he looks for robjects names cotaining 'robject' part and checks
        # result.
        self.search_input().send_keys("robject")
        self.search_button().click()

        self.browser.find_element_by_class_name("robject_1")
        self.browser.find_element_by_class_name("robject_2")
        table_rows = self.browser.find_elements_by_class_name("row")

        self.assertEqual(len(table_rows), 2)

    def test_annonymous_user_cant_request_search_url(self):
        # create sample project
        proj = Project.objects.create(name="project_1")

        # User would like to know if he can reach search robjecs url without
        # logging. He requests search url.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj.name}/robjects/search")

        # Now he sees permission denied message.
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(body.text, "403 Forbidden")

    def test_user_search_for_robject_name_using_case_insensitivity(self):
        # User want to search robject using its name, but he dont know what is
        # exact letter case. He knows that name contains letter with both cases
        # and that searching suppouse to be case insensitve. User decide to use
        # all upper case letters and then all lower case letters and compare
        # results.

        # Make set up for robjects page.
        user, proj = self.project_set_up_using_default_data()

        # Create sample robject.
        robj = Robject.objects.create(name="RoBjEcT_1")

        # User goes to robjects page.
        self.browser.get(self.live_server_url +
                         f"/projects/{proj.name}/robjects/")

        # User enters name using lower case letters.
        self.search_input().send_keys("robject_1")
        self.search_button().click()
        # User looks for results.
        self.browser.find_element_by_css_selector(f".row.{robj.name}")

        # User enters name using upper case letters.
        self.search_input().send_keys("ROBJECT_1")
        self.search_button().click()

        # User looks for results.
        self.browser.find_element_by_css_selector(f".row.{robj.name}")

    def test_user_can_search_robject_using_full_author_username(self):
        user, proj = self.project_set_up_using_default_data()

        # Create sample robject.
        # User goes to robjects page.
        robj = self.create_sample_robject_and_go_to_robjects_page(
            project=proj, author=user, name="robject_1")

        # He sees sample robject in table.
        self.look_for_robject_row(f".row.{robj.name}")

        # User heard he can search robject using author name. He want to
        # confirm that.
        self.send_query(robj.author.username)

        # Yeah, its still there!
        self.look_for_robject_row(f".row.{robj.name}")

    def test_user_can_search_robjet_using_fragment_of_athor_username(self):
        user, proj = self.project_set_up_using_default_data()

        # Create sample robject.
        # User goes to robjects page.
        robj = self.create_sample_robject_and_go_to_robjects_page(
            project=proj, author=user, name="robject_1")

        # He sees sample robject in table.
        self.look_for_robject_row(f".row.{robj.name}")

        # User heard he can search robject using fragment of author username.
        # He want to confirm that.
        self.send_query(user.username[0:-1])

        # Yeah, its still there!
        self.look_for_robject_row(f".row.{robj.name}")

    def test_user_can_search_robject_using_case_insensitive_full_author_username(self):
        user, proj = self.project_set_up_using_default_data()

        # Create sample robject.
        # User goes to robjects page.
        robj = self.create_sample_robject_and_go_to_robjects_page(
            project=proj, author=user, name="robject_1")

        # He sees sample robject in table.
        self.look_for_robject_row(f".row.{robj.name}")

        # User heard he can search robject using fragment of author username.
        # He want to confirm that.
        self.send_query("UsErNaMe")

        # Yeah, its still there!
        self.look_for_robject_row(f".row.{robj.name}")

    def test_user_limits_number_of_fields_to_search(self):
        pass

    def test_user_narrows_the_search_to_the_date_range(self):
        pass
