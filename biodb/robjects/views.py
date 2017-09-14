"""Views for robject search."""
import re
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import CharField
from biodb.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import ForeignKey
from django.db.models import TextField
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View
from openpyxl import Workbook
# from projects.mixin import ExportViewMixin
from projects.models import Project
from robjects.models import Robject
# from robjects.models import Tag
from weasyprint import CSS
from weasyprint import HTML

# Create your views here.


def robjects_list_view(request, project_name):
    if not request.user.is_authenticated():
        raise PermissionDenied
    project = Project.objects.get(name=project_name)
    robject_list = Robject.objects.filter(project=project)
    return render(request, "projects/robjects_list.html",
                  {"robject_list": robject_list, "project_name": project_name})


# TODO: Add multipleObjectMixin to inherit by this class??
class SearchRobjectsView(LoginRequiredMixin, View):
    """View to show filtered list of objects."""
    model = Robject

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


class RobjectDetailView(DetailView):
    model = Robject
    template_name = "robjects/robject_detail.html"
    def get(self, request, *args, **kwargs):
        """A base view for displaying a list of objects."""
        # check if project exists
        try:
            request.session['_succes_url'] = self.request.build_absolute_uri()

            pk = kwargs['pk']
            robject = Robject.objects.get(id=pk)
            # add project to view attributes
            self.robject = robject
        except Robject.DoesNotExist:
            raise Http404
        return super(RobjectDetailView, self).get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        """
        Overwrite orginal qs and add filtering by project_name
        """
        # original queryset
        qs = super(RobjectDetailView, self).get_queryset(*args, **kwargs)
        # print(self.args) # empty

        pk = self.kwargs['pk']
        robject = Robject.objects.get(id=pk)
        # add project to view attributes
        self.robject = robject

        qs = qs.filter(name=robject.name)
        return qs

    def get_context_data(self, **kwargs):
        context = super(RobjectDetailView, self).get_context_data(**kwargs)

        context['robject'] = self.robject
        return context
