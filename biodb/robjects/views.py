"""Views for robject search."""
import re
from biodb.mixins import LoginRequiredMixin, LoginPermissionRequiredMixin, BreadcrumbsMixin
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import TextField
from django.db.models import Q
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import View, CreateView, DeleteView, UpdateView, ListView
from projects.models import Project
from robjects.models import Tag
from projects.mixins import ExportViewMixin
from robjects.models import Robject, Name
from django import forms
from django_addanother.widgets import AddAnotherWidgetWrapper
from django.core.urlresolvers import reverse, resolve
from django.shortcuts import redirect
from django_addanother.views import CreatePopupMixin
from django.utils.decorators import method_decorator
from guardian.mixins import LoginRequiredMixin as GuardianLoginRequiredMixin
from guardian.mixins import PermissionRequiredMixin
from biodb import settings
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from samples.views import SampleListView
from django.core.urlresolvers import Resolver404
from django.contrib import messages
from django.utils.translation import ugettext as _
from tools.history import generate_versions
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
# Create your views here.


def robjects_list_view(request, project_name):
    if not request.user.is_authenticated():
        raise PermissionDenied
    project = Project.objects.get(name=project_name)
    robject_list = Robject.objects.filter(project=project)
    return render(request, "projects/robjects_list.html",
                  {"robject_list": robject_list, "project_name": project_name})


class RobjectListView(LoginPermissionRequiredMixin, BreadcrumbsMixin, ListView):
    template_name = "projects/robjects_list.html"
    context_object_name = "robject_list"
    permissions_required = ["can_visit_project"]

    def get_queryset(self):
        project = self.get_permission_object()
        qs = Robject.objects.filter(project=project)
        return qs

    def get_context_data(self):
        context = super().get_context_data()
        context["project_name"] = self.kwargs["project_name"]
        return context

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs["project_name"])
        return project


class ExportExcelView(LoginPermissionRequiredMixin, ExportViewMixin, View):
    model = Robject
    queryset = None
    permissions_required = ["can_visit_project"]

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        return project

    def get(self, request, project_name, *args, **kwargs):
        robjects_pk = list(request.GET.values())
        qs = Robject.objects.filter(pk__in=robjects_pk)
        if not qs:
            messages.error(request, "No robject selected!")
            return redirect(self.get_success_url())

        return self.export_to_excel(qs, is_relation=True,
                                    one_to_one=True, many_to_one=True,
                                    exclude_fields=['sample'])

    def get_success_url(self):
        return reverse("projects:robjects:robjects_list", kwargs={
            "project_name": self.kwargs["project_name"]})


class RobjectPDFeView(LoginPermissionRequiredMixin, View, ExportViewMixin):
    model = Robject
    pdf_template_name = "robjects/robject_raport_pdf.html"
    pdf_css_name = 'robjects/css/raport_pdf.css'
    css_sufix = '/robjects'
    permissions_required = ["can_visit_project"]

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        return project

    def get(self, request, project_name, *args, **kwargs):
        self.object_list = Robject.objects.filter(pk__in=request.GET.values())
        if not self.object_list:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                'class_name': self.__class__.__name__,
            })
        return self.export_to_pdf(self.object_list)


# TODO: Add multipleObjectMixin to inherit by this class??
class SearchRobjectsView(LoginPermissionRequiredMixin, View):
    """View to show filtered list of objects."""
    model = Robject
    permissions_required = ["can_visit_project"]

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        return project

    def get(self, request, project_name):
        query = request.GET.get("query")

        queryset = self.perform_search(query, project_name)

        return render(request, "projects/robjects_list.html",
                      {"robject_list": queryset, "project_name": project_name})

    def normalize_query(self, query_string,
                        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        """Splits the query string in invidual keywords, getting rid of
           unecessary spaces and grouping quoted words together.

            Args:
                query_string (str): string with query words

            Example:
                >>> normalize_query('some random  words "with   quotes  "
                                    and   spaces  ')
                ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

            Returns:
                the list of words
        """
        terms = [normspace(
            ' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
        return terms

    def perform_search(self, query, project_name):
        """Perform search for robjects using given query.

        Normalize search string and divede them into search terms.
        Create list of search queris for CharField and TextField.

        Args:
            query (str): Search string provieded by user
            project_name (str): name of the project (auto).

        Returns:
            model objects list (list): filtered list of model objects
            model is filtered based on Q objects Complex SQL expression
            in Django (see Django docs) and project_name
        """
        # normalize query string and get the list of words (search terms)
        terms = self.normalize_query(query)
        # get list of text fields
        text_fields = [f for f in self.model._meta.get_fields() if isinstance(
            f, (CharField, TextField))]
        # get the list of foreig fields
        foreign_fields = [
            f for f in self.model._meta.get_fields()
            if isinstance(f, ForeignKey)]
        # get dict with ForeigKey field as key and list of Char/Text fields
        # that are in related model as a argument
        foreign_models_fields = {}
        for foreign_field in foreign_fields:
            fmodel = self.model._meta.get_field(
                '%s' % foreign_field.name).rel.to
            foreign_models_fields[foreign_field] = [
                f for f in fmodel._meta.fields
                if isinstance(f, (CharField, TextField))]

        # define Q() objects to use or on queries
        qs = Q()
        # iterate over all search terms and create the queries
        # for model text fields and foreign text fields
        for term in terms:
            # get queries for Char/Text fields
            queries = [Q(**{'%s__icontains' % f.name: term})
                       for f in text_fields]
            # exted queries by foreign fields
            if foreign_models_fields:
                for foreign_field, model_fields \
                        in foreign_models_fields.items():
                    queries += [Q(**{'%s__%s__icontains' %
                                     (foreign_field.name, f.name): term})
                                for f in model_fields]
            # perform logical OR on queries
            if queries:
                for qs_query in queries:
                    qs = qs | qs_query
        # project required

        return self.model.objects.filter(qs, project__name=project_name)


class RobjectCreateView(LoginPermissionRequiredMixin, BreadcrumbsMixin, CreateView):
    model = Robject
    template_name = "robjects/robject_create.html"
    permissions_required = ["can_visit_project", "can_modify_project"]
    breadcrumb_model = "robject"
    breadcrumb_action = "create"
    # raise_exception = True

    def get_form_class(self):
        form = forms.modelform_factory(
            model=Robject, fields="__all__",
            exclude=["create_by", "create_date", "modify_by"],
            widgets={
                "names": AddAnotherWidgetWrapper(
                    widget=forms.SelectMultiple,
                    add_related_url=reverse(
                        "projects:robjects:names_create", kwargs={"project_name": self.kwargs["project_name"]})
                ),
                "tags":  AddAnotherWidgetWrapper(
                    widget=forms.SelectMultiple,
                    add_related_url=reverse(
                        "projects:robjects:tags_create", kwargs={"project_name": self.kwargs["project_name"]})
                ),
                'project': forms.HiddenInput()
            })
        return form

    def get_success_url(self):
        return reverse("projects:robjects:robjects_list", kwargs={"project_name": self.kwargs["project_name"]})

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs["project_name"])
        return project

    def get(self, request, *args, **kwargs):
        Name.objects.filter(robjects=None).delete()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        robject = form.save()
        robject.create_by = self.request.user
        robject.modify_by = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        return {
            "project": Project.objects.get(name=self.kwargs["project_name"])
        }


class NameCreateView(CreatePopupMixin, CreateView):
    model = Name
    fields = "__all__"
    template_name = "robjects/names_create.html"

    def get(self, request, *args, **kwargs):
        from urllib.parse import urlparse
        previously_visited_path = urlparse(
            request.META.get("HTTP_REFERER", None)).path
        try:
            url_name = resolve(previously_visited_path).url_name
            if url_name == "robject_create" or url_name == "robject_edit":
                return super().get(request, *args, **kwargs)
        except Resolver404:
            return HttpResponseBadRequest(
                "<h1>Error 400</h1><p>Form available from robject form only</p>")


class TagCreateView(CreatePopupMixin, CreateView):
    model = Tag
    fields = ["name"]
    template_name = "robjects/tags_create.html"
    success_url = "/"  # not required, for test pass purpose only!

    def get(self, request, *args, **kwargs):
        from urllib.parse import urlparse
        previously_visited_path = urlparse(
            request.META.get("HTTP_REFERER", None)).path
        try:
            url_name = resolve(previously_visited_path).url_name
            if url_name == "robject_create" or url_name == "robject_edit":
                return super().get(request, *args, **kwargs)
        except Resolver404:
            return HttpResponseBadRequest(
                "<h1>Error 400</h1><p>Form available from robject form only</p>")

    def form_valid(self, form):
        tag = form.save()
        tag.project = Project.objects.get(name=self.kwargs["project_name"])
        return super().form_valid(form)


class RobjectSamplesList(SampleListView):
    permissions_required = ["can_visit_project"]

    def get_queryset(self):
        """
        Overwrite orginal qs and add filtering by robject
        """
        # original queryset
        project_name = self.kwargs['project_name']
        robject_id = self.kwargs['robject_id']
        qs = super(RobjectSamplesList, self).get_queryset()

        qs = qs.filter(robject__pk=robject_id)
        return qs


class RobjectDeleteView(LoginPermissionRequiredMixin, BreadcrumbsMixin, DeleteView):
    model = Robject
    context_object_name = "robjects"
    permissions_required = ["can_visit_project", "can_modify_project"]

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        return project

    def get_object(self):
        ids = self.request.GET.values()
        qs = self.model.objects.filter(pk__in=ids)
        return qs

    def get_success_url(self):
        return reverse("projects:robjects:robjects_list", kwargs=self.kwargs)


class RobjectEditView(RobjectCreateView, BreadcrumbsMixin,  UpdateView):
    pk_url_kwarg = "robject_id"
    permissions_required = ["can_visit_project", "can_modify_project"]
    breadcrumb_action = "edit"

    def form_valid(self, form):
        robject = form.save()
        robject.modify_by = self.request.user
        robject.save()
        return redirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class RobjectHistoryView(LoginPermissionRequiredMixin, BreadcrumbsMixin, DetailView):
    """View to show historical records of robject.

    Views show in table all changes made on object.
    Changes are prsented in github style.
    """
    model = Robject
    template_name = "robjects/robject_history.html"
    permissions_required = ["can_visit_project"]
    pk_url_kwarg = "robject_id"

    def get_permission_object(self):
        p = get_object_or_404(Project, name=self.kwargs["project_name"])
        return p

    def get_context_data(self, **kwargs):
        """Add CustomHistory objects as versions to context."""
        context = super(RobjectHistoryView, self).get_context_data(**kwargs)
        # get robject
        robject = self.get_object()
        # get all simple history versions
        robject_history = robject.history.all()
        # use history_tools for built logic on top of versions (prepare for
        # table)
        exclude_fields = ["create_date", "modify_date"]
        versions = generate_versions(robject_history, exclude=exclude_fields)
        # create table
        context["versions"] = versions
        return context
