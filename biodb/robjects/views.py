"""Views for robject search."""
import re
from biodb.mixins import LoginRequiredMixin
from bs4 import BeautifulSoup
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import TextField
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from biodb.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View
from projects.models import Project
from robjects.models import Robject
from robjects.models import Tag
from django.http import HttpResponse
# Create your views here.


def robjects_export_to_excel_view(request, *args, **kwargs):
    ''' Function handle export to excel view '''
    from openpyxl import Workbook
    from datetime import datetime

    # help function
    def str_is_html(field):
        ''' Returns true if passed string contains html. '''
        field = str(field)
        return bool(BeautifulSoup(field, "html.parser").find())

    pk = kwargs['pk']
    robject = Robject.objects.get(pk=pk)
    # create workbook
    wb = Workbook()
    # capture active worksheet
    ws = wb.active
    # filling first row by fields names
    ws.append([field.name for field in Robject._meta.fields] + ["files"])
    temp = list()
    for field in robject._meta.fields:
        # holding field value
        field_value = getattr(robject, field.name)

        # formating date
        if isinstance(field_value, datetime):
            temp.append(field_value.strftime("%Y-%m-%d %H:%M"))
            continue

        if str_is_html(field_value):
            only_text = BeautifulSoup(
                str(field_value), 'html.parser').text
            temp.append(only_text.strip())
            continue

        # append to container
        temp.append(str(field_value))

        # adding cline row to excel
    ws.append(temp)
    output = HttpResponse()
    # preparing output
    file_name = "report.xlsx"
    output['Content-Disposition'] = 'attachment; filename=' + file_name
    # saving workbook to output
    wb.save(output)
    return output


def robjects_list_view(request, project_name):
    if not request.user.is_authenticated():
        raise PermissionDenied
    project = Project.objects.get(name=project_name)
    robject_list = Robject.objects.filter(project=project)
    return render(request, "projects/robjects_list.html",
                  {"robject_list": robject_list, "project_name": project_name})


class SearchRobjectsView(LoginRequiredMixin, View):
    # TODO: Add multipleObjectMixin to inherit by this class??
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

        # project reqired
        return self.model.objects.filter(qs, project__name=project_name)


class RobjectDetailView(DetailView):
    model = Robject
