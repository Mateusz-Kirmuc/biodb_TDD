from django.core.urlresolvers import reverse
from django.test import tag
from django.utils import timezone
from functional_tests.base import FunctionalTest
from projects.models import Project
import time
from guardian.shortcuts import assign_perm
from robjects.models import Robject, Name, Tag
from selenium.common.exceptions import NoSuchElementException
import datetime


@tag('slow')
class RobjectCreateTestCase(FunctionalTest):
    def get_robject_create_url(self):
        return self.live_server_url +\
            reverse("projects:robjects:robject_create",
                    kwargs={"project_name": "project_1"})

    # TODO: check if below method is accurate and relevant
    def get_robject_form_url(self, proj):
        return self.live_server_url + \
            reverse("projects:robjects:robject_create", args=(proj.name,))

    def add_related_name(self, name):
        """User click in plus button, switch to popup, add related and get back.
        """
        plus_btn = self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_names + a")
        plus_btn.click()

        self.switch_to_popup()
        name_input = self.browser.find_element_by_css_selector(
            "input[name='name']")
        name_input.send_keys(name)
        self.browser.find_element_by_css_selector(
            "input[type='submit']").click()
        self.switch_to_main()

    def add_related_tag(self, name):
        """ User click in plus button, switch to popup, add related and get back.
        """
        plus_btn = self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_tags + a")
        plus_btn.click()

        self.switch_to_popup()
        name_input = self.browser.find_element_by_css_selector(
            "input[name='name']")
        name_input.send_keys(name)
        self.browser.find_element_by_css_selector(
            "input[type='submit']").click()
        self.switch_to_main()

    def check_for_related_name_in_input(self, name):
        option_tag = self.wait_for(lambda: self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_names option:last-child"))

        self.assertEqual(option_tag.text, name)

    def check_for_related_tag_in_input(self, name):
        option_tag = self.wait_for(lambda: self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_tags option:last-child"))

        self.assertEqual(option_tag.text, name)

    def fill_cke_field(self, field_id, text):
        """ User add some text to cke field.
        """
        frame = self.browser.find_element_by_css_selector(
            f"#{field_id} iframe")
        self.browser.switch_to_frame(frame)
        self.browser.find_element_by_tag_name(
            "body").send_keys(text)
        self.switch_to_main()

    def set_project_and_user(self, project_name="project_1",
                             username="USERNAME", password="PASSWORD"):
        proj = Project.objects.create(name=project_name)
        user = self.login_user(username, password)
        assign_perm("can_visit_project", user, proj)
        assign_perm("can_modify_project", user, proj)

        return proj, user

    def get_last_robject(self):
        r = Robject.objects.last()
        return r

    def get_robject_create_page(self):
        self.browser.get(self.get_robject_create_url())

    def submit_and_assert_valid_redirect(self):
        self.browser.find_element_by_css_selector("button").click()

        self.assertEqual(
            self.browser.current_url,
            self.live_server_url +
            reverse("projects:robjects:robjects_list",
                    kwargs={"project_name": "project_1"})
        )

    def test_user_enter_wrong_slug_in_url(self):
        self.not_matching_url_slug_helper(self.ROBJECT_CREATE_URL)

    def test_user_fill_full_form_with_multiple_names_tags_and_files(self):
        proj, user = self.set_project_and_user()

        # User wants to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # First, user create related models. He start from add two additional
        # names. User clicks in plus button next to name select input.
        self.add_related_name("NAME1")

        # User gets back to main window. He noticed new name in select input.
        self.check_for_related_name_in_input("NAME1")

        # Now, he create another name.
        self.add_related_name("NAME2")
        self.wait_for(
            lambda: self.check_for_related_name_in_input("NAME2"))

        # User create tags.
        self.add_related_tag("TAG1")
        self.check_for_related_tag_in_input(name="TAG1")

        self.add_related_tag(name="TAG2")
        time.sleep(3)
        self.check_for_related_tag_in_input(name="TAG2")

        # Time for robject files. The same story, user add two files.
        # TODO: find a way to test adding files

        # User now fill all CKE widget fields.
        # Notes
        self.fill_cke_field(field_id="cke_id_notes", text="These are notes.")

        # Ref seq
        self.fill_cke_field(field_id="cke_id_ref_seq",
                            text="These are ref seq.")

        # Mod seq
        self.fill_cke_field(field_id="cke_id_mod_seq",
                            text="These are mod seq.")

        # Description
        self.fill_cke_field(field_id="cke_id_description",
                            text="This is description.")

        # Bibliography
        self.fill_cke_field(field_id="cke_id_bibliography",
                            text="This is bibliography.")

        # Ref commmercial
        self.fill_cke_field(field_id="cke_id_ref_commercial",
                            text="This is ref commercial.")

        # Ref clinical
        self.fill_cke_field(field_id="cke_id_ref_clinical",
                            text="This is ref clinical.")

        # User now fill all other fields.
        # Name
        self.browser.find_element_by_id("id_name").send_keys("robject1")

        # Author
        author_option = self.browser.find_element_by_xpath(
            "//option[contains(text(), 'USERNAME')]")
        author_option.click()

        # Ligand
        self.browser.find_element_by_css_selector(
            "#id_ligand").send_keys("ligand")

        # Receptor
        self.browser.find_element_by_css_selector(
            "#id_receptor").send_keys("receptor")

        # Finally user submit his form and looks for redirection.
        self.submit_and_assert_valid_redirect()

        # Confirm that created robject lives in db.
        r = self.get_last_robject()

        # Related fields
        self.assertEqual(list(r.names.all()), list(
            Name.objects.filter(robjects=r)))
        self.assertEqual(list(r.tags.all()), list(
            Tag.objects.filter(robjects=r)))

        # CKE fields
        self.assertEqual(r.notes, "<p>These are notes.</p>")
        self.assertEqual(r.ref_seq, "<p>These are ref seq.</p>")
        self.assertEqual(r.mod_seq, "<p>These are mod seq.</p>")
        self.assertEqual(r.description, "<p>This is description.</p>")
        self.assertEqual(r.bibliography, "<p>This is bibliography.</p>")
        self.assertEqual(r.ref_commercial, "<p>This is ref commercial.</p>")
        self.assertEqual(r.ref_clinical, "<p>This is ref clinical.</p>")

        # other fields
        self.assertEqual(r.name, "robject1")
        self.assertEqual(r.author, user)
        self.assertEqual(r.ligand, "ligand")
        self.assertEqual(r.receptor, "receptor")

    def test_user_fill_form_without_less_likely_fields(self):
        proj, user = self.set_project_and_user()

        # User wants to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # First he fills relational fields. He add additional name and select
        # it.
        self.add_related_name(name="NAME_007")
        self.check_for_related_name_in_input(name="NAME_007")

        # Next, he creates new tag and select it.
        self.add_related_tag(name="important")
        self.check_for_related_tag_in_input(name="important")

        # Now, user fills CKE fields.

        # Ref seq
        self.fill_cke_field(field_id="cke_id_ref_seq",
                            text="Remember, remember the 5th of November,")

        # Mod seq
        self.fill_cke_field(field_id="cke_id_mod_seq",
                            text="Gunpowder, treason and plot.")

        # Ref commmercial
        self.fill_cke_field(field_id="cke_id_ref_commercial",
                            text="I see of no reason why gunpoder treason,")

        # Ref clinical
        self.fill_cke_field(field_id="cke_id_ref_clinical",
                            text="Should ever be forgot.")

        # Finally, user fills rest of fields.
        # Name
        self.browser.find_element_by_id("id_name").send_keys("ROBJ_NAME")

        # Author
        author_option = self.browser.find_element_by_xpath(
            "//option[contains(text(), 'USERNAME')]")
        author_option.click()

        # Ligand
        self.browser.find_element_by_css_selector(
            "#id_ligand").send_keys("XYZ_123")

        # Receptor
        self.browser.find_element_by_css_selector(
            "#id_receptor").send_keys("mTOR")

        # User, clicks for submit and looks for redirect.
        self.submit_and_assert_valid_redirect()

        # CONFIRMATION OF ROBJECT IN DB
        r = self.get_last_robject()

        # Related fields
        self.assertEqual(list(r.names.all()), list(
            Name.objects.filter(robjects=r)))
        self.assertEqual(list(r.tags.all()), list(
            Tag.objects.filter(robjects=r)))
        # CKE fields
        self.assertEqual(
            r.ref_seq, "<p>Remember, remember the 5th of November,</p>")
        self.assertEqual(r.mod_seq, "<p>Gunpowder, treason and plot.</p>")
        self.assertEqual(r.ref_commercial,
                         "<p>I see of no reason why gunpoder treason,</p>")
        self.assertEqual(r.ref_clinical, "<p>Should ever be forgot.</p>")

        # other fields
        self.assertEqual(r.name, "ROBJ_NAME")
        self.assertEqual(r.author, user)
        self.assertEqual(r.ligand, "XYZ_123")
        self.assertEqual(r.receptor, "mTOR")

    def test_user_creates_new_additional_names_but_not_picks_all(self):
        proj, user = self.set_project_and_user()

        # User wants to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User creates three new additional names.
        self.add_related_name(name="name_1")
        self.add_related_name(name="name_2")
        self.add_related_name(name="name_3")

        # After that, he unselect one of them.
        self.browser.find_element_by_xpath(
            "//option[contains(text(), 'name_2')]").click()

        # Next, he fills three other fields.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("robject_name")

        self.browser.find_element_by_css_selector(
            "#id_ligand").send_keys("C6H12O6")

        self.browser.find_element_by_css_selector(
            "#id_receptor").send_keys("USP8")

        # Finally, user submit form and looks for redirection.
        self.submit_and_assert_valid_redirect()

        # CONFIRMATION OF ROBJECT IN DB
        r = self.get_last_robject()

        # related Names
        self.assertEqual(
            list(r.names.all()),
            [Name.objects.get(name="name_1"), Name.objects.get(name="name_3")]
        )

        # other fields
        self.assertEqual(r.name, "robject_name")
        self.assertEqual(r.ligand, "C6H12O6")
        self.assertEqual(r.receptor, "USP8")

    def test_user_creates_new_tag_and_chooses_existing(self):
        proj, user = self.set_project_and_user()

        # CREATE PREEXISTING TAG
        Tag.objects.create(name="pre_tag", project=proj)

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User create new tag.
        self.add_related_tag(name="new_tag")

        # User additionally pick preexisting tag from select menu.
        self.browser.find_element_by_xpath(
            "//option[contains(text(), 'pre_tag')]").click()

        # At last he fill name field.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("cool_robject_name")

        # Finally, submits button and looks for redirection.
        self.submit_and_assert_valid_redirect()

        # ASSERT ROBJECT IN DB
        r = self.get_last_robject()

        self.assertEqual(
            list(r.tags.all()),
            [Tag.objects.get(name="pre_tag"), Tag.objects.get(name="new_tag")]
        )

    def test_annonymous_user_try_to_get_to_robject_form(self):
        proj = Project.objects.create(name="project_1")

        # Annonymous user tries to get robject form.
        self.browser.get(self.get_robject_create_url())

        # He is redirect to login page.
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url +
            reverse("login") + f"?next=/projects/{proj.name}/robjects/create/"
        )

    def test_user_without_project_mod_permission_try_to_get_robject_form(self):
        proj = Project.objects.create(name="project_1")

        # CREATE USER WITH PROJECT VISIT PERMISSION ONLY
        user = self.login_user(username="limit_user", password="password")
        assign_perm("can_visit_project", user, proj)

        # User without project-modification permission tries to get robject
        # form.
        self.get_robject_create_page()

        # He gets 403 permission denied message.
        message = self.browser.find_element_by_css_selector("h1")
        self.assertEqual(
            message.text, "User doesn't have permission: can modify project")

    def test_user_fill_form_without_name(self):
        # USER AND PROJ SETTING
        proj, user = self.set_project_and_user()

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User fill some fields but forgot to fill name.
        self.browser.find_element_by_css_selector(
            "#id_ligand").send_keys("random_ligand")
        self.browser.find_element_by_css_selector(
            "#id_receptor").send_keys("random_receptor")

        # He submits the form.
        self.browser.find_element_by_tag_name("button").click()

        # User sees name error message.
        self.assertEqual(self.browser.current_url,
                         self.get_robject_create_url())

        # el = self.browser.find_element_by_css_selector(
        #     "#id_name:focus:required:invalid")

        # All previously filled fields remains filled.
        self.assertEqual(
            self.browser.find_element_by_css_selector(
                "#id_ligand").get_attribute("value"),
            "random_ligand"
        )
        self.assertEqual(
            self.browser.find_element_by_css_selector(
                "#id_receptor").get_attribute("value"),
            "random_receptor"
        )

    def test_user_uses_name_for_robj_already_used_in_different_proj(self):
        # SET PROJECT AND USER
        self.set_project_and_user()

        # CREATE DIFFERENT PROJ
        proj_dif = Project.objects.create(name="proj_diff")

        # CREATE RANDOM ROBJECT
        Robject.objects.create(name="taken_name", project=proj_dif)

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User picks name already existing but in different project.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("taken_name")

        # He submits the form. Nothing happens, form process normally.
        self.submit_and_assert_valid_redirect()

    def test_user_pick_already_taken_name_for_robj(self):
        # SET PROJECT AND USER
        proj, user = self.set_project_and_user()

        # CREATE RANDOM ROBJECT
        Robject.objects.create(project=proj, name="xyz")

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User picks project and name already existing in this project.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("xyz")

        # He fill some additional fields.
        self.browser.find_element_by_css_selector(
            "#id_ligand").send_keys("random_ligand")
        self.browser.find_element_by_css_selector(
            "#id_receptor").send_keys("random_receptor")

        # He submits the form.
        self.browser.find_element_by_tag_name("button").click()

        # User sees name validation error message above name field.
        error = self.browser.find_element_by_css_selector("ul.errorlist li")
        self.assertEqual(
            error.text, "Robject with this Name and Project already exists.")

        # All previously filled fields remains unchanged.
        self.assertEqual(
            self.browser.find_element_by_css_selector(
                "#id_ligand").get_attribute("value"),
            "random_ligand"
        )
        self.assertEqual(
            self.browser.find_element_by_css_selector(
                "#id_receptor").get_attribute("value"),
            "random_receptor"
        )

    def test_user_tries_add_additional_name_that_already_exists_in_project(self):
        # SET PROJECT AND USER
        self.set_project_and_user()

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User adds additional name to robject.
        self.add_related_name(name="pre_name")

        # Now, user wants to add new additional name, but enter the same text.
        plus_btn = self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_names + a")
        plus_btn.click()
        self.switch_to_popup()

        # User creates new additional name.
        name_input = self.browser.find_element_by_css_selector(
            "input[name='name']")
        name_input.send_keys("pre_name")
        self.browser.find_element_by_css_selector(
            "input[type='submit']").click()

        # User sees error message.
        error = self.browser.find_element_by_css_selector("ul.errorlist li")
        self.assertEqual(
            error.text, "Name with this Name already exists.")

    def test_user_tries_add_tag_that_already_exists_in_project(self):
        # SET PROJECT AND USER
        proj, user = self.set_project_and_user()

        # CREATE SAMPLE TAG
        t = Tag.objects.create(name="sample_tag", project=proj)

        # User want to create new robject. He goes to robject form page.
        self.get_robject_create_page()

        # User try to add additional tag to robject. He clicks plus button and
        # switch to popup form.
        plus_btn = self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_tags + a")
        plus_btn.click()
        self.switch_to_popup()

        # He tries to create name that already exists.
        name_input = self.browser.find_element_by_css_selector(
            "input[name='name']")
        name_input.send_keys(t.name)
        self.browser.find_element_by_css_selector(
            "input[type='submit']").click()

        # User sees error message.
        error = self.browser.find_element_by_css_selector("ul.errorlist li")
        self.assertEqual(
            error.text, "Tag with this Name already exists.")

    def test_user_create_addit_names_but_refresh_page_instead_submit_form(self):
        # SET UP
        self.set_project_and_user()

        # User visits robject page.
        self.get_robject_create_page()

        # He adds two new additional names.
        self.add_related_name("name_one")
        self.add_related_name("name_two")
        names_in_select_tag = self.browser.find_elements_by_css_selector(
            "#id_names option")
        self.assertEqual(len(names_in_select_tag), 2)

        # User refresh page instead of submit form.
        self.browser.refresh()

        # He sees empty name select tag.
        names_in_select_tag = self.browser.find_elements_by_css_selector(
            "#id_names option")
        self.assertEqual(len(names_in_select_tag), 0)

    def test_user_come_back_to_form_after_submit_and_see_empty_names_tag(self):
        # SET UP
        self.set_project_and_user()

        # User visits robject page.
        self.get_robject_create_page()

        # He adds two new additional names.
        self.add_related_name("name_one")
        self.add_related_name("name_two")

        # Then he adds main name.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("whatever")

        # Finally, submit form.
        self.submit_and_assert_valid_redirect()

        # Now, user comes back to form to find out that names select element is
        # empty.
        names_in_select_tag = self.browser.find_elements_by_css_selector(
            "#id_names option")
        self.assertEqual(len(names_in_select_tag), 0)

    def test_some_fields_are_hidden_but_auto_assigned(self):
        # SET UP
        proj, user = self.set_project_and_user()

        # User visits robject page.
        self.get_robject_create_page()

        # He specify name.
        self.browser.find_element_by_css_selector(
            "#id_name").send_keys("whatever")

        # User cant see any of following fields: create_by,
        # create_date, modify_by or modify_date fields
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector("#id_create_by")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector("#id_modify_by")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector("#id_create_date")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector("#id_modify_date")

        # Now user submits form.
        moment_of_creation = timezone.now()
        self.submit_and_assert_valid_redirect()

        # He realize that even though he didnt specify project, create_by,
        # create_date, modify_by or modify_date fields, and even has a chance to
        # do it in form, those fields are specified by default.
        r = Robject.objects.last()
        self.assertEqual(r.project, proj)
        self.assertEqual(r.create_by, user)
        self.assertEqual(r.modify_by, user)

        # NOTE: this assertions may crash becouse they depends on time execution
        # which may vary
        # Consider this solution: https://bytes.vokal.io/almost-equal/
        self.assertAlmostEqual(
            r.create_date, moment_of_creation, delta=datetime.timedelta(seconds=1))
        self.assertAlmostEqual(
            r.modify_date, moment_of_creation, delta=datetime.timedelta(seconds=1))

    def test_Tag_form_not_contains_project_field_but_project_is_auto_assigned(self):
        # SET UP
        proj, user = self.set_project_and_user()

        # User visits robject page.
        self.get_robject_create_page()

        # He clicks plus button and goes to popup form.
        plus_btn = self.browser.find_element_by_css_selector(
            f".related-widget-wrapper select#id_tags + a")
        plus_btn.click()
        self.switch_to_popup()

        # User can't see project field.
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector("#id_project")

        # Next he enters tag's name and clicks submit.
        name_input = self.browser.find_element_by_css_selector(
            "input[name='name']")
        name_input.send_keys("test_name")
        self.browser.find_element_by_css_selector(
            "input[type='submit']").click()
        self.switch_to_main()
        # He realize that even though he didnt specify project this field is
        # assigned anyway to project from url.
        t = Tag.objects.last()
        self.assertEqual(t.project, proj)

    def test_user_opens_Name_popup_using_url_not_plus_button(self):
        # SET UP
        proj, user = self.set_project_and_user()

        name_popup_url = self.live_server_url + \
            reverse("projects:robjects:names_create", args=(proj.name,))

        # User wants to visit popup form using url adress instead of plus
        # button.
        self.browser.get(name_popup_url)

        # He sees 400 bad request error and message explains error.
        error = self.browser.find_element_by_css_selector("h1")
        message = self.browser.find_element_by_css_selector("p")

        self.assertEqual(error.text, "Error 400")
        self.assertEqual(message.text, "Form available from robject form only")

    def test_user_opens_Tag_popup_using_url_not_plus_button(self):
        # SET UP
        proj, user = self.set_project_and_user()

        tag_popup_url = self.live_server_url + \
            reverse("projects:robjects:tags_create", args=(proj.name,))

        # User wants to visit popup form using url adress instead of plus
        # button.
        self.browser.get(tag_popup_url)

        # He sees 400 bad request error and message explains error.
        error = self.browser.find_element_by_css_selector("h1")
        message = self.browser.find_element_by_css_selector("p")

        self.assertEqual(error.text, "Error 400")
        self.assertEqual(message.text, "Form available from robject form only")
